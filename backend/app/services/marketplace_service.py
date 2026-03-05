import re
import uuid
from decimal import Decimal, ROUND_HALF_UP

from sqlalchemy import func, text
from sqlalchemy.orm import Session

from app.core.errors import AppException
from app.core.pro import require_pro
from app.models.marketplace import (
    Cart,
    CartItem,
    MarketplaceSettings,
    Part,
    PurchaseOrder,
    PurchaseOrderItem,
    Supplier,
    SupplierPart,
    WorkshopSupplier,
)
from app.models.enums import (
    AvailabilityStatus,
    CartStatus,
    DeliveryMode,
    PricingMode,
    PurchaseOrderStatus,
)
from app.models.service import Service, ServiceItem
from app.models.user import User


_ALLOWED_ORDER_STATUS = {
    PurchaseOrderStatus.draft.value,
    PurchaseOrderStatus.placed.value,
    PurchaseOrderStatus.confirmed.value,
    PurchaseOrderStatus.shipped.value,
    PurchaseOrderStatus.delivered.value,
    PurchaseOrderStatus.canceled.value,
}


def _q2(v: Decimal) -> Decimal:
    return (v or Decimal("0")).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def _money_str(v: Decimal) -> str:
    return f"{_q2(v):.2f}"


def _parse_money(s: str | None) -> Decimal:
    raw = (s or "0").strip()
    raw = raw.replace("R$", "").replace(" ", "")
    raw = raw.replace(".", "").replace(",", ".") if "," in raw else raw
    try:
        return _q2(Decimal(raw))
    except Exception:
        raise AppException(400, "invalid_money", "Valor inválido.")


def _advisory_lock_for_workshop(db: Session, workshop_id: uuid.UUID) -> None:
    key = int(workshop_id.int % 2147483647)
    db.execute(text("SELECT pg_advisory_xact_lock(:k)"), {"k": key})


def _next_po_number(db: Session, workshop_id: uuid.UUID) -> str:
    _advisory_lock_for_workshop(db, workshop_id)
    last = (
        db.query(PurchaseOrder.order_number)
        .filter(PurchaseOrder.workshop_id == workshop_id)
        .order_by(PurchaseOrder.created_at.desc())
        .limit(1)
        .scalar()
    )
    n = 0
    if last:
        m = re.search(r"(\d+)$", str(last))
        if m:
            try:
                n = int(m.group(1))
            except ValueError:
                n = 0
    n += 1
    return f"PO-{n:06d}"


def get_settings(db: Session, *, workshop_id: uuid.UUID) -> MarketplaceSettings:
    s = (
        db.query(MarketplaceSettings)
        .filter(MarketplaceSettings.workshop_id == workshop_id)
        .one_or_none()
    )
    if s:
        return s
    s = MarketplaceSettings(
        workshop_id=workshop_id,
        allow_attendant_purchase=False,
        default_markup_percent=20,
        pricing_mode=PricingMode.markup.value,
        pro_feature_enabled=False,
    )
    db.add(s)
    db.flush()
    db.refresh(s)
    return s


def _ensure_pro(db: Session, *, user: User) -> None:
    settings = get_settings(db, workshop_id=user.workshop_id)
    if not settings.pro_feature_enabled:
        raise AppException(402, "pro_required", "Desbloqueie o Marketplace Pro para usar esta função.")
    require_pro(db, workshop_id=user.workshop_id)


def search_parts(
    db: Session,
    *,
    user: User,
    query: str | None,
    category: str | None,
    brand: str | None,
    limit: int = 30,
) -> list[Part]:
    q = db.query(Part).filter(Part.active.is_(True))

    if query:
        term = query.strip()
        if term:
            like = f"%{term.lower()}%"
            q = q.filter(
                func.lower(Part.name).like(like)
                | func.lower(Part.sku).like(like)
                | func.lower(Part.brand).like(like)
            )

    if category:
        cat = category.strip().lower()
        if cat:
            q = q.filter(func.lower(Part.category) == cat)

    if brand:
        b = brand.strip().lower()
        if b:
            q = q.filter(func.lower(Part.brand) == b)

    return q.order_by(Part.name.asc()).limit(max(1, min(int(limit), 60))).all()


def get_part(db: Session, *, part_id: uuid.UUID) -> Part:
    p = db.query(Part).filter(Part.id == part_id, Part.active.is_(True)).one_or_none()
    if not p:
        raise AppException(404, "not_found", "Peça não encontrada.")
    return p


def get_offers(db: Session, *, user: User, part_id: uuid.UUID) -> list[dict]:
    _ensure_pro(db, user=user)

    rows = (
        db.query(SupplierPart, Supplier)
        .join(Supplier, Supplier.id == SupplierPart.supplier_id)
        .join(WorkshopSupplier, WorkshopSupplier.supplier_id == Supplier.id)
        .filter(
            WorkshopSupplier.workshop_id == user.workshop_id,
            WorkshopSupplier.active.is_(True),
            SupplierPart.part_id == part_id,
        )
        .order_by(SupplierPart.price.asc())
        .all()
    )

    out = []
    for sp, sup in rows:
        out.append(
            {
                "supplier_id": sup.id,
                "supplier_name": sup.name,
                "price": _money_str(Decimal(sp.price or 0)),
                "availability_status": sp.availability_status or AvailabilityStatus.unknown.value,
                "lead_time_days": sp.lead_time_days,
                "supplier_sku": sp.supplier_sku,
            }
        )
    return out


def _get_or_create_open_cart(db: Session, *, user: User) -> Cart:
    _ensure_pro(db, user=user)

    cart = (
        db.query(Cart)
        .filter(
            Cart.workshop_id == user.workshop_id,
            Cart.created_by_user_id == user.id,
            Cart.status == CartStatus.open.value,
        )
        .order_by(Cart.updated_at.desc())
        .first()
    )
    if cart:
        return cart

    cart = Cart(
        workshop_id=user.workshop_id,
        status=CartStatus.open.value,
        created_by_user_id=user.id,
    )
    db.add(cart)
    db.flush()
    db.refresh(cart)
    return cart


def get_cart(db: Session, *, user: User) -> dict:
    cart = _get_or_create_open_cart(db, user=user)

    items = (
        db.query(CartItem, Part, Supplier)
        .join(Part, Part.id == CartItem.part_id)
        .outerjoin(Supplier, Supplier.id == CartItem.chosen_supplier_id)
        .filter(CartItem.cart_id == cart.id)
        .order_by(Part.name.asc())
        .all()
    )

    out_items = []
    for ci, p, s in items:
        out_items.append(
            {
                "id": ci.id,
                "part_id": p.id,
                "sku": p.sku,
                "name": p.name,
                "brand": p.brand,
                "category": p.category,
                "qty": int(ci.qty or 0),
                "chosen_supplier_id": ci.chosen_supplier_id,
                "chosen_supplier_name": (s.name if s else None),
                "unit_price_snapshot": _money_str(Decimal(ci.unit_price_snapshot or 0)),
            }
        )

    return {
        "id": cart.id,
        "status": cart.status,
        "items": out_items,
        "created_at": cart.created_at,
        "updated_at": cart.updated_at,
    }


def add_cart_item(
    db: Session,
    *,
    user: User,
    part_id: uuid.UUID,
    qty: int,
    chosen_supplier_id: uuid.UUID | None,
    unit_price_snapshot: str | None,
) -> dict:
    cart = _get_or_create_open_cart(db, user=user)
    p = get_part(db, part_id=part_id)

    q = int(qty or 1)
    if q < 1 or q > 999:
        raise AppException(400, "invalid_qty", "Quantidade inválida.")

    ups = _parse_money(unit_price_snapshot) if unit_price_snapshot is not None else None

    if chosen_supplier_id:
        ok = (
            db.query(WorkshopSupplier.id)
            .filter(
                WorkshopSupplier.workshop_id == user.workshop_id,
                WorkshopSupplier.supplier_id == chosen_supplier_id,
                WorkshopSupplier.active.is_(True),
            )
            .first()
        )
        if not ok:
            raise AppException(400, "invalid_supplier", "Fornecedor inválido.")

        offer = (
            db.query(SupplierPart)
            .filter(SupplierPart.supplier_id == chosen_supplier_id, SupplierPart.part_id == p.id)
            .one_or_none()
        )
        if offer:
            ups = _q2(Decimal(offer.price or 0))
        elif ups is None:
            raise AppException(400, "missing_price", "Preço do fornecedor não encontrado.")
    else:
        if ups is None:
            if p.suggested_price is not None:
                ups = _q2(Decimal(p.suggested_price))
            else:
                raise AppException(400, "missing_price", "Informe o preço para adicionar ao carrinho.")

    existing = (
        db.query(CartItem)
        .filter(CartItem.cart_id == cart.id, CartItem.part_id == p.id)
        .one_or_none()
    )
    if existing:
        existing.qty = int(existing.qty or 0) + q
        existing.chosen_supplier_id = chosen_supplier_id
        existing.unit_price_snapshot = ups
        db.add(existing)
        db.flush()
    else:
        ci = CartItem(
            cart_id=cart.id,
            part_id=p.id,
            qty=q,
            chosen_supplier_id=chosen_supplier_id,
            unit_price_snapshot=ups,
        )
        db.add(ci)
        db.flush()

    db.add(cart)
    db.flush()
    return get_cart(db, user=user)


def _role_can_purchase(db: Session, *, user: User) -> None:
    settings = get_settings(db, workshop_id=user.workshop_id)
    if user.role == "admin":
        return
    if settings.allow_attendant_purchase:
        return
    raise AppException(403, "forbidden", "Somente admin pode finalizar pedidos de compra.")


def create_order_from_cart(
    db: Session,
    *,
    user: User,
    supplier_id: uuid.UUID,
    delivery_mode: str,
    delivery_address: str | None,
    shipping: str,
    discount: str,
) -> PurchaseOrder:
    _ensure_pro(db, user=user)
    _role_can_purchase(db, user=user)

    cart = _get_or_create_open_cart(db, user=user)

    items = (
        db.query(CartItem, Part)
        .join(Part, Part.id == CartItem.part_id)
        .filter(CartItem.cart_id == cart.id)
        .all()
    )
    if not items:
        raise AppException(400, "empty_cart", "Carrinho vazio.")

    sup_ok = (
        db.query(WorkshopSupplier.id)
        .filter(
            WorkshopSupplier.workshop_id == user.workshop_id,
            WorkshopSupplier.supplier_id == supplier_id,
            WorkshopSupplier.active.is_(True),
        )
        .first()
    )
    if not sup_ok:
        raise AppException(400, "invalid_supplier", "Fornecedor inválido.")

    for ci, _p in items:
        if ci.chosen_supplier_id != supplier_id:
            raise AppException(
                400,
                "mixed_suppliers",
                "Escolha um fornecedor único para finalizar (ajuste os itens do carrinho).",
            )

    dm = (delivery_mode or "").strip().lower()
    if dm not in {DeliveryMode.delivery.value, DeliveryMode.pickup.value}:
        raise AppException(400, "invalid_delivery_mode", "delivery_mode inválido.")

    po_number = _next_po_number(db, user.workshop_id)

    subtotal = Decimal("0.00")
    for ci, _p in items:
        subtotal += _q2(Decimal(ci.unit_price_snapshot or 0) * Decimal(int(ci.qty or 0)))

    shipping_d = _parse_money(shipping)
    discount_d = _parse_money(discount)
    total = _q2(subtotal + shipping_d - discount_d)
    if total < 0:
        total = Decimal("0.00")

    po = PurchaseOrder(
        workshop_id=user.workshop_id,
        order_number=po_number,
        status=PurchaseOrderStatus.placed.value,
        supplier_id=supplier_id,
        subtotal=_q2(subtotal),
        shipping=_q2(shipping_d),
        discount=_q2(discount_d),
        total=_q2(total),
        delivery_mode=dm,
        delivery_address=(delivery_address or "").strip() or None,
        created_by_user_id=user.id,
    )
    db.add(po)
    db.flush()

    for ci, p in items:
        unit = _q2(Decimal(ci.unit_price_snapshot or 0))
        qty = int(ci.qty or 0)
        t = _q2(unit * Decimal(qty))
        poi = PurchaseOrderItem(
            purchase_order_id=po.id,
            part_id=p.id,
            qty=qty,
            unit_price=unit,
            total_price=t,
        )
        db.add(poi)

    cart.status = CartStatus.ordered.value
    db.add(cart)
    db.flush()
    db.refresh(po)
    return po


def list_orders(db: Session, *, user: User, limit: int = 40) -> list[PurchaseOrder]:
    _ensure_pro(db, user=user)
    return (
        db.query(PurchaseOrder)
        .filter(PurchaseOrder.workshop_id == user.workshop_id)
        .order_by(PurchaseOrder.created_at.desc())
        .limit(max(1, min(int(limit), 80)))
        .all()
    )


def get_order(db: Session, *, user: User, order_id: uuid.UUID) -> PurchaseOrder:
    _ensure_pro(db, user=user)
    po = (
        db.query(PurchaseOrder)
        .filter(PurchaseOrder.workshop_id == user.workshop_id, PurchaseOrder.id == order_id)
        .one_or_none()
    )
    if not po:
        raise AppException(404, "not_found", "Pedido não encontrado.")
    return po


def order_to_dict(db: Session, *, user: User, po: PurchaseOrder) -> dict:
    sup = db.query(Supplier).filter(Supplier.id == po.supplier_id).one_or_none()
    items = (
        db.query(PurchaseOrderItem, Part)
        .join(Part, Part.id == PurchaseOrderItem.part_id)
        .filter(PurchaseOrderItem.purchase_order_id == po.id)
        .order_by(Part.name.asc())
        .all()
    )
    out_items = []
    for it, p in items:
        out_items.append(
            {
                "id": it.id,
                "part_id": p.id,
                "sku": p.sku,
                "name": p.name,
                "qty": int(it.qty or 0),
                "unit_price": _money_str(Decimal(it.unit_price or 0)),
                "total_price": _money_str(Decimal(it.total_price or 0)),
            }
        )

    return {
        "id": po.id,
        "order_number": po.order_number,
        "status": po.status,
        "supplier_id": po.supplier_id,
        "supplier_name": (sup.name if sup else "Fornecedor"),
        "subtotal": _money_str(Decimal(po.subtotal or 0)),
        "shipping": _money_str(Decimal(po.shipping or 0)),
        "discount": _money_str(Decimal(po.discount or 0)),
        "total": _money_str(Decimal(po.total or 0)),
        "delivery_mode": po.delivery_mode,
        "delivery_address": po.delivery_address,
        "created_at": po.created_at,
        "updated_at": po.updated_at,
        "items": out_items,
    }


def update_order_status(db: Session, *, user: User, order_id: uuid.UUID, status: str) -> PurchaseOrder:
    _ensure_pro(db, user=user)
    _role_can_purchase(db, user=user)

    po = get_order(db, user=user, order_id=order_id)
    st = (status or "").strip().lower()
    if st not in _ALLOWED_ORDER_STATUS:
        raise AppException(400, "invalid_status", "Status inválido.")
    po.status = st
    db.add(po)
    db.flush()
    db.refresh(po)
    return po


def _get_service(db: Session, *, user: User, service_id: uuid.UUID) -> Service:
    s = (
        db.query(Service)
        .filter(Service.workshop_id == user.workshop_id, Service.id == service_id)
        .one_or_none()
    )
    if not s:
        raise AppException(404, "not_found", "Serviço não encontrado.")
    return s


def _recalc_service_totals(db: Session, *, service: Service) -> None:
    subtotal = (
        db.query(func.coalesce(func.sum(ServiceItem.total_price), 0))
        .filter(ServiceItem.workshop_id == service.workshop_id, ServiceItem.service_id == service.id)
        .scalar()
    )
    subtotal_d = _q2(Decimal(subtotal or 0))
    labor = _q2(Decimal(service.labor_amount or 0))
    total_d = _q2(subtotal_d + labor)
    service.subtotal_amount = subtotal_d
    service.total_amount = total_d
    db.add(service)
    db.flush()


def _add_service_item(
    db: Session,
    *,
    user: User,
    service: Service,
    description: str,
    qty: int,
    unit_price: Decimal,
    part_id: uuid.UUID | None,
) -> ServiceItem:
    q = int(qty or 1)
    if q < 1 or q > 999:
        raise AppException(400, "invalid_qty", "Quantidade inválida.")
    desc = (description or "").strip()
    if not desc:
        raise AppException(400, "invalid_description", "Descrição inválida.")
    if len(desc) > 160:
        desc = desc[:160]

    unit = _q2(Decimal(unit_price or 0))
    total = _q2(unit * Decimal(q))

    it = ServiceItem(
        workshop_id=user.workshop_id,
        service_id=service.id,
        part_id=part_id,
        description=desc,
        qty=q,
        unit_price=unit,
        total_price=total,
    )
    db.add(it)
    db.flush()
    _recalc_service_totals(db, service=service)
    db.refresh(it)
    return it


def add_order_items_to_service(
    db: Session,
    *,
    user: User,
    service_id: uuid.UUID,
    order_id: uuid.UUID,
) -> Service:
    _ensure_pro(db, user=user)

    po = get_order(db, user=user, order_id=order_id)
    if po.status != PurchaseOrderStatus.delivered.value:
        raise AppException(400, "order_not_delivered", "Só é possível adicionar itens após o pedido estar DELIVERED.")

    s = _get_service(db, user=user, service_id=service_id)

    settings = get_settings(db, workshop_id=user.workshop_id)
    markup = int(settings.default_markup_percent or 0)

    items = (
        db.query(PurchaseOrderItem, Part)
        .join(Part, Part.id == PurchaseOrderItem.part_id)
        .filter(PurchaseOrderItem.purchase_order_id == po.id)
        .all()
    )
    if not items:
        return s

    for it, p in items:
        unit = _q2(Decimal(it.unit_price or 0))
        if settings.pricing_mode == PricingMode.markup.value and markup > 0:
            unit = _q2(unit * (Decimal("1.00") + (Decimal(markup) / Decimal("100"))))

        _add_service_item(
            db,
            user=user,
            service=s,
            description=f"{p.name}".strip(),
            qty=int(it.qty or 1),
            unit_price=unit,
            part_id=p.id,
        )

    _recalc_service_totals(db, service=s)
    db.refresh(s)
    return s