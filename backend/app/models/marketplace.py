import uuid
from decimal import Decimal

from sqlalchemy import Boolean, ForeignKey, Integer, Numeric, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TenantMixin, TimestampMixin, UUIDPrimaryKeyMixin
from app.models.enums import (
    AvailabilityStatus,
    CartStatus,
    CommissionAppliesTo,
    CommissionMode,
    DeliveryMode,
    PricingMode,
    PurchaseOrderStatus,
)


class Part(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "parts"
    __table_args__ = (
        UniqueConstraint("sku", name="uq_parts_sku"),
    )

    sku: Mapped[str] = mapped_column(String(60), nullable=False)
    name: Mapped[str] = mapped_column(String(160), nullable=False)
    brand: Mapped[str] = mapped_column(String(80), nullable=False, default="")
    category: Mapped[str] = mapped_column(String(80), nullable=False, default="")
    vehicle_compat: Mapped[str] = mapped_column(Text, nullable=False, default="")

    cost_price: Mapped[Decimal | None] = mapped_column(Numeric(12, 2), nullable=True)
    suggested_price: Mapped[Decimal | None] = mapped_column(Numeric(12, 2), nullable=True)

    active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    offers = relationship("SupplierPart", back_populates="part")


class Supplier(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "suppliers"
    __table_args__ = (
        UniqueConstraint("name", name="uq_suppliers_name"),
    )

    name: Mapped[str] = mapped_column(String(160), nullable=False)
    whatsapp: Mapped[str | None] = mapped_column(String(30), nullable=True)
    cnpj: Mapped[str | None] = mapped_column(String(30), nullable=True)
    city: Mapped[str | None] = mapped_column(String(80), nullable=True)

    offers = relationship("SupplierPart", back_populates="supplier")


class WorkshopSupplier(Base, UUIDPrimaryKeyMixin, TenantMixin, TimestampMixin):
    __tablename__ = "workshop_suppliers"
    __table_args__ = (
        UniqueConstraint("workshop_id", "supplier_id", name="uq_workshop_suppliers_workshop_supplier"),
    )

    supplier_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("suppliers.id"), nullable=False, index=True)
    active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)


class SupplierPart(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "supplier_parts"
    __table_args__ = (
        UniqueConstraint("supplier_id", "part_id", name="uq_supplier_parts_supplier_part"),
    )

    supplier_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("suppliers.id"), nullable=False, index=True)
    part_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("parts.id"), nullable=False, index=True)

    supplier_sku: Mapped[str | None] = mapped_column(String(80), nullable=True)

    price: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False, default=0)
    availability_status: Mapped[str] = mapped_column(String(20), nullable=False, default=AvailabilityStatus.unknown.value)
    lead_time_days: Mapped[int | None] = mapped_column(Integer, nullable=True)

    supplier = relationship("Supplier", back_populates="offers")
    part = relationship("Part", back_populates="offers")


class WorkshopFavoritePart(Base, UUIDPrimaryKeyMixin, TenantMixin, TimestampMixin):
    __tablename__ = "workshop_favorite_parts"
    __table_args__ = (
        UniqueConstraint("workshop_id", "part_id", name="uq_workshop_favorite_parts_workshop_part"),
    )

    part_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("parts.id"), nullable=False, index=True)


class Cart(Base, UUIDPrimaryKeyMixin, TenantMixin, TimestampMixin):
    __tablename__ = "carts"

    status: Mapped[str] = mapped_column(String(20), nullable=False, default=CartStatus.open.value)
    created_by_user_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True, index=True)

    items = relationship("CartItem", back_populates="cart", cascade="all, delete-orphan")


class CartItem(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "cart_items"
    __table_args__ = (
        UniqueConstraint("cart_id", "part_id", name="uq_cart_items_cart_part"),
    )

    cart_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("carts.id"), nullable=False, index=True)
    part_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("parts.id"), nullable=False, index=True)

    qty: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    chosen_supplier_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("suppliers.id"), nullable=True, index=True)
    unit_price_snapshot: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False, default=0)

    cart = relationship("Cart", back_populates="items")


class PurchaseOrder(Base, UUIDPrimaryKeyMixin, TenantMixin, TimestampMixin):
    __tablename__ = "purchase_orders"
    __table_args__ = (
        UniqueConstraint("workshop_id", "order_number", name="uq_purchase_orders_workshop_order_number"),
    )

    order_number: Mapped[str] = mapped_column(String(20), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default=PurchaseOrderStatus.draft.value)

    supplier_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("suppliers.id"), nullable=False, index=True)

    subtotal: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False, default=0)
    shipping: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False, default=0)
    discount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False, default=0)
    total: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False, default=0)

    delivery_mode: Mapped[str] = mapped_column(String(20), nullable=False, default=DeliveryMode.delivery.value)
    delivery_address: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_by_user_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True, index=True)

    items = relationship("PurchaseOrderItem", back_populates="purchase_order", cascade="all, delete-orphan")


class PurchaseOrderItem(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "purchase_order_items"
    __table_args__ = (
        UniqueConstraint("purchase_order_id", "part_id", name="uq_purchase_order_items_po_part"),
    )

    purchase_order_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("purchase_orders.id"), nullable=False, index=True)
    part_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("parts.id"), nullable=False, index=True)

    qty: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    unit_price: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False, default=0)
    total_price: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False, default=0)

    purchase_order = relationship("PurchaseOrder", back_populates="items")


class MarketplaceSettings(Base, TenantMixin, TimestampMixin):
    __tablename__ = "marketplace_settings"

    workshop_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("workshops.id"), primary_key=True)

    allow_attendant_purchase: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    default_markup_percent: Mapped[int] = mapped_column(Integer, nullable=False, default=20)
    pricing_mode: Mapped[str] = mapped_column(String(20), nullable=False, default=PricingMode.markup.value)
    pro_feature_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)


class CommissionRule(Base, UUIDPrimaryKeyMixin, TenantMixin, TimestampMixin):
    __tablename__ = "commission_rules"

    mode: Mapped[str] = mapped_column(String(20), nullable=False, default=CommissionMode.percent.value)
    value: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False, default=0)

    applies_to: Mapped[str] = mapped_column(String(20), nullable=False, default=CommissionAppliesTo.all.value)

    category: Mapped[str | None] = mapped_column(String(80), nullable=True)
    supplier_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("suppliers.id"), nullable=True, index=True)