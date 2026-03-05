import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.auth import get_current_user
from app.db.deps import get_db
from app.models.user import User
from app.schemas.marketplace import (
    AddCartItemIn,
    CartOut,
    PartOfferOut,
    PartOut,
    PurchaseOrderOut,
    PurchaseOrderStatusUpdate,
    CheckoutFromCartIn,
)
from app.services.marketplace_service import (
    add_cart_item,
    add_order_items_to_service,
    create_order_from_cart,
    get_cart,
    get_offers,
    get_order,
    get_part,
    list_orders,
    order_to_dict,
    search_parts,
    update_order_status,
)

router = APIRouter(prefix="/marketplace", tags=["marketplace"])


@router.get("/parts", response_model=list[PartOut])
def parts(
    query: str | None = Query(default=None),
    category: str | None = Query(default=None),
    brand: str | None = Query(default=None),
    limit: int = Query(default=30, ge=1, le=60),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    rows = search_parts(db, user=user, query=query, category=category, brand=brand, limit=limit)
    out = []
    for p in rows:
        out.append(
            PartOut(
                id=p.id,
                sku=p.sku,
                name=p.name,
                brand=p.brand,
                category=p.category,
                vehicle_compat=p.vehicle_compat,
                active=p.active,
                suggested_price=(f"{p.suggested_price:.2f}" if p.suggested_price is not None else None),
            )
        )
    return out


@router.get("/parts/{part_id}", response_model=PartOut)
def part_detail(
    part_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    pid = uuid.UUID(part_id)
    p = get_part(db, part_id=pid)
    return PartOut(
        id=p.id,
        sku=p.sku,
        name=p.name,
        brand=p.brand,
        category=p.category,
        vehicle_compat=p.vehicle_compat,
        active=p.active,
        suggested_price=(f"{p.suggested_price:.2f}" if p.suggested_price is not None else None),
    )


@router.get("/parts/{part_id}/offers", response_model=list[PartOfferOut])
def offers(
    part_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    pid = uuid.UUID(part_id)
    rows = get_offers(db, user=user, part_id=pid)
    return [PartOfferOut(**r) for r in rows]


@router.post("/cart/items", response_model=CartOut)
def add_to_cart(
    body: AddCartItemIn,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    cart = add_cart_item(
        db,
        user=user,
        part_id=body.part_id,
        qty=body.qty,
        chosen_supplier_id=body.chosen_supplier_id,
        unit_price_snapshot=body.unit_price_snapshot,
    )
    db.commit()
    return CartOut(**cart)


@router.get("/cart", response_model=CartOut)
def cart(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    c = get_cart(db, user=user)
    return CartOut(**c)


@router.post("/orders/from-cart", response_model=PurchaseOrderOut)
def order_from_cart(
    body: CheckoutFromCartIn,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    po = create_order_from_cart(
        db,
        user=user,
        supplier_id=body.supplier_id,
        delivery_mode=body.delivery_mode,
        delivery_address=body.delivery_address,
        shipping=body.shipping,
        discount=body.discount,
    )
    db.commit()
    out = order_to_dict(db, user=user, po=po)
    return PurchaseOrderOut(**out)


@router.get("/orders", response_model=list[PurchaseOrderOut])
def orders(
    limit: int = Query(default=40, ge=1, le=80),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    rows = list_orders(db, user=user, limit=limit)
    out = []
    for po in rows:
        out.append(PurchaseOrderOut(**order_to_dict(db, user=user, po=po)))
    return out


@router.get("/orders/{order_id}", response_model=PurchaseOrderOut)
def order_detail(
    order_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    oid = uuid.UUID(order_id)
    po = get_order(db, user=user, order_id=oid)
    return PurchaseOrderOut(**order_to_dict(db, user=user, po=po))


@router.post("/orders/{order_id}/status", response_model=PurchaseOrderOut)
def order_status(
    order_id: str,
    body: PurchaseOrderStatusUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    oid = uuid.UUID(order_id)
    po = update_order_status(db, user=user, order_id=oid, status=body.status)
    db.commit()
    return PurchaseOrderOut(**order_to_dict(db, user=user, po=po))


@router.post("/orders/{order_id}/add-to-service/{service_id}")
def add_delivered_items_to_service(
    order_id: str,
    service_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    oid = uuid.UUID(order_id)
    sid = uuid.UUID(service_id)
    s = add_order_items_to_service(db, user=user, service_id=sid, order_id=oid)
    db.commit()
    return {"ok": True, "service_id": str(s.id)}