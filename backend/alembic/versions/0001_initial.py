"""initial

Revision ID: 0001_initial
Revises:
Create Date: 2026-03-03

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "0001_initial"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "workshops",
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("phone", sa.String(length=30), nullable=True),
        sa.Column("city", sa.String(length=80), nullable=True),
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )

    op.create_table(
        "suppliers",
        sa.Column("name", sa.String(length=160), nullable=False),
        sa.Column("whatsapp", sa.String(length=30), nullable=True),
        sa.Column("cnpj", sa.String(length=30), nullable=True),
        sa.Column("city", sa.String(length=80), nullable=True),
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.UniqueConstraint("name", name="uq_suppliers_name"),
    )

    op.create_table(
        "parts",
        sa.Column("sku", sa.String(length=60), nullable=False),
        sa.Column("name", sa.String(length=160), nullable=False),
        sa.Column("brand", sa.String(length=80), nullable=False, server_default=""),
        sa.Column("category", sa.String(length=80), nullable=False, server_default=""),
        sa.Column("vehicle_compat", sa.Text(), nullable=False, server_default=""),
        sa.Column("cost_price", sa.Numeric(precision=12, scale=2), nullable=True),
        sa.Column("suggested_price", sa.Numeric(precision=12, scale=2), nullable=True),
        sa.Column("active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.UniqueConstraint("sku", name="uq_parts_sku"),
    )

    op.create_table(
        "users",
        sa.Column("workshop_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("email", sa.String(length=180), nullable=False),
        sa.Column("role", sa.String(length=20), nullable=False, server_default="attendant"),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["workshop_id"], ["workshops.id"], name="fk_users_workshop_id_workshops"),
        sa.UniqueConstraint("workshop_id", "email", name="uq_users_workshop_email"),
    )
    op.create_index("ix_users_workshop_id", "users", ["workshop_id"], unique=False)

    op.create_table(
        "refresh_tokens",
        sa.Column("workshop_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("jti", sa.String(length=64), nullable=False),
        sa.Column("token_hash", sa.String(length=255), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_used_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], name="fk_refresh_tokens_user_id_users"),
        sa.ForeignKeyConstraint(["workshop_id"], ["workshops.id"], name="fk_refresh_tokens_workshop_id_workshops"),
        sa.UniqueConstraint("jti", name="uq_refresh_tokens_jti"),
    )
    op.create_index("ix_refresh_tokens_workshop_id", "refresh_tokens", ["workshop_id"], unique=False)
    op.create_index("ix_refresh_tokens_user_id", "refresh_tokens", ["user_id"], unique=False)

    op.create_table(
        "customers",
        sa.Column("name", sa.String(length=140), nullable=False),
        sa.Column("phone", sa.String(length=30), nullable=False),
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("workshop_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["workshop_id"], ["workshops.id"], name="fk_customers_workshop_id_workshops"),
        sa.UniqueConstraint("workshop_id", "phone", name="uq_customers_workshop_phone"),
    )
    op.create_index("ix_customers_workshop_id", "customers", ["workshop_id"], unique=False)

    op.create_table(
        "vehicles",
        sa.Column("plate", sa.String(length=16), nullable=False),
        sa.Column("customer_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("workshop_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["customer_id"], ["customers.id"], name="fk_vehicles_customer_id_customers"),
        sa.ForeignKeyConstraint(["workshop_id"], ["workshops.id"], name="fk_vehicles_workshop_id_workshops"),
        sa.UniqueConstraint("workshop_id", "plate", name="uq_vehicles_workshop_plate"),
    )
    op.create_index("ix_vehicles_workshop_id", "vehicles", ["workshop_id"], unique=False)
    op.create_index("ix_vehicles_customer_id", "vehicles", ["customer_id"], unique=False)

    op.create_table(
        "services",
        sa.Column("vehicle_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("customer_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="in_progress"),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("labor_amount", sa.Numeric(precision=12, scale=2), nullable=False, server_default="0"),
        sa.Column("subtotal_amount", sa.Numeric(precision=12, scale=2), nullable=False, server_default="0"),
        sa.Column("total_amount", sa.Numeric(precision=12, scale=2), nullable=False, server_default="0"),
        sa.Column("created_by_user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("workshop_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["customer_id"], ["customers.id"], name="fk_services_customer_id_customers"),
        sa.ForeignKeyConstraint(["created_by_user_id"], ["users.id"], name="fk_services_created_by_user_id_users"),
        sa.ForeignKeyConstraint(["vehicle_id"], ["vehicles.id"], name="fk_services_vehicle_id_vehicles"),
        sa.ForeignKeyConstraint(["workshop_id"], ["workshops.id"], name="fk_services_workshop_id_workshops"),
    )
    op.create_index("ix_services_workshop_id", "services", ["workshop_id"], unique=False)
    op.create_index("ix_services_vehicle_id", "services", ["vehicle_id"], unique=False)
    op.create_index("ix_services_customer_id", "services", ["customer_id"], unique=False)
    op.create_index("ix_services_created_by_user_id", "services", ["created_by_user_id"], unique=False)

    op.create_table(
        "service_items",
        sa.Column("service_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("part_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("description", sa.String(length=160), nullable=False),
        sa.Column("qty", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("unit_price", sa.Numeric(precision=12, scale=2), nullable=False, server_default="0"),
        sa.Column("total_price", sa.Numeric(precision=12, scale=2), nullable=False, server_default="0"),
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("workshop_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["part_id"], ["parts.id"], name="fk_service_items_part_id_parts"),
        sa.ForeignKeyConstraint(["service_id"], ["services.id"], name="fk_service_items_service_id_services"),
        sa.ForeignKeyConstraint(["workshop_id"], ["workshops.id"], name="fk_service_items_workshop_id_workshops"),
    )
    op.create_index("ix_service_items_workshop_id", "service_items", ["workshop_id"], unique=False)
    op.create_index("ix_service_items_service_id", "service_items", ["service_id"], unique=False)
    op.create_index("ix_service_items_part_id", "service_items", ["part_id"], unique=False)

    op.create_table(
        "quotes",
        sa.Column("service_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("quote_number", sa.String(length=20), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="draft"),
        sa.Column("public_token", sa.String(length=64), nullable=False),
        sa.Column("snapshot", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("html_cache", sa.Text(), nullable=True),
        sa.Column("subtotal_amount", sa.Numeric(precision=12, scale=2), nullable=False, server_default="0"),
        sa.Column("total_amount", sa.Numeric(precision=12, scale=2), nullable=False, server_default="0"),
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("workshop_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["service_id"], ["services.id"], name="fk_quotes_service_id_services"),
        sa.ForeignKeyConstraint(["workshop_id"], ["workshops.id"], name="fk_quotes_workshop_id_workshops"),
        sa.UniqueConstraint("public_token", name="uq_quotes_public_token"),
        sa.UniqueConstraint("workshop_id", "quote_number", name="uq_quotes_workshop_quote_number"),
    )
    op.create_index("ix_quotes_workshop_id", "quotes", ["workshop_id"], unique=False)
    op.create_index("ix_quotes_service_id", "quotes", ["service_id"], unique=False)

    op.create_table(
        "return_rules",
        sa.Column("name", sa.String(length=80), nullable=False, server_default="Retorno"),
        sa.Column("days_after", sa.Integer(), nullable=False, server_default="180"),
        sa.Column("active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("workshop_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["workshop_id"], ["workshops.id"], name="fk_return_rules_workshop_id_workshops"),
    )
    op.create_index("ix_return_rules_workshop_id", "return_rules", ["workshop_id"], unique=False)

    op.create_table(
        "returns",
        sa.Column("customer_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("vehicle_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("service_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("due_date", sa.DateTime(timezone=True), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="pending"),
        sa.Column("whatsapp_message", sa.Text(), nullable=True),
        sa.Column("sent_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("done_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("workshop_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["customer_id"], ["customers.id"], name="fk_returns_customer_id_customers"),
        sa.ForeignKeyConstraint(["service_id"], ["services.id"], name="fk_returns_service_id_services"),
        sa.ForeignKeyConstraint(["vehicle_id"], ["vehicles.id"], name="fk_returns_vehicle_id_vehicles"),
        sa.ForeignKeyConstraint(["workshop_id"], ["workshops.id"], name="fk_returns_workshop_id_workshops"),
    )
    op.create_index("ix_returns_workshop_id", "returns", ["workshop_id"], unique=False)
    op.create_index("ix_returns_customer_id", "returns", ["customer_id"], unique=False)
    op.create_index("ix_returns_vehicle_id", "returns", ["vehicle_id"], unique=False)
    op.create_index("ix_returns_service_id", "returns", ["service_id"], unique=False)

    op.create_table(
        "payments",
        sa.Column("service_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("amount", sa.Numeric(precision=12, scale=2), nullable=False, server_default="0"),
        sa.Column("method", sa.String(length=30), nullable=False, server_default="cash"),
        sa.Column("paid_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("workshop_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["service_id"], ["services.id"], name="fk_payments_service_id_services"),
        sa.ForeignKeyConstraint(["workshop_id"], ["workshops.id"], name="fk_payments_workshop_id_workshops"),
    )
    op.create_index("ix_payments_workshop_id", "payments", ["workshop_id"], unique=False)
    op.create_index("ix_payments_service_id", "payments", ["service_id"], unique=False)

    op.create_table(
        "subscriptions",
        sa.Column("plan", sa.String(length=10), nullable=False, server_default="basic"),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="expired"),
        sa.Column("kiwify_transaction_id", sa.String(length=120), nullable=True),
        sa.Column("current_period_end", sa.DateTime(timezone=True), nullable=True),
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("workshop_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["workshop_id"], ["workshops.id"], name="fk_subscriptions_workshop_id_workshops"),
        sa.UniqueConstraint("workshop_id", name="uq_subscriptions_workshop"),
    )
    op.create_index("ix_subscriptions_kiwify_transaction_id", "subscriptions", ["kiwify_transaction_id"], unique=False)
    op.create_index("ix_subscriptions_workshop_id", "subscriptions", ["workshop_id"], unique=False)

    op.create_table(
        "workshop_suppliers",
        sa.Column("supplier_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("workshop_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["supplier_id"], ["suppliers.id"], name="fk_workshop_suppliers_supplier_id_suppliers"),
        sa.ForeignKeyConstraint(["workshop_id"], ["workshops.id"], name="fk_workshop_suppliers_workshop_id_workshops"),
        sa.UniqueConstraint("workshop_id", "supplier_id", name="uq_workshop_suppliers_workshop_supplier"),
    )
    op.create_index("ix_workshop_suppliers_workshop_id", "workshop_suppliers", ["workshop_id"], unique=False)
    op.create_index("ix_workshop_suppliers_supplier_id", "workshop_suppliers", ["supplier_id"], unique=False)

    op.create_table(
        "supplier_parts",
        sa.Column("supplier_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("part_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("supplier_sku", sa.String(length=80), nullable=True),
        sa.Column("price", sa.Numeric(precision=12, scale=2), nullable=False, server_default="0"),
        sa.Column("availability_status", sa.String(length=20), nullable=False, server_default="unknown"),
        sa.Column("lead_time_days", sa.Integer(), nullable=True),
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["part_id"], ["parts.id"], name="fk_supplier_parts_part_id_parts"),
        sa.ForeignKeyConstraint(["supplier_id"], ["suppliers.id"], name="fk_supplier_parts_supplier_id_suppliers"),
        sa.UniqueConstraint("supplier_id", "part_id", name="uq_supplier_parts_supplier_part"),
    )
    op.create_index("ix_supplier_parts_supplier_id", "supplier_parts", ["supplier_id"], unique=False)
    op.create_index("ix_supplier_parts_part_id", "supplier_parts", ["part_id"], unique=False)

    op.create_table(
        "workshop_favorite_parts",
        sa.Column("part_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("workshop_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["part_id"], ["parts.id"], name="fk_workshop_favorite_parts_part_id_parts"),
        sa.ForeignKeyConstraint(["workshop_id"], ["workshops.id"], name="fk_workshop_favorite_parts_workshop_id_workshops"),
        sa.UniqueConstraint("workshop_id", "part_id", name="uq_workshop_favorite_parts_workshop_part"),
    )
    op.create_index("ix_workshop_favorite_parts_workshop_id", "workshop_favorite_parts", ["workshop_id"], unique=False)
    op.create_index("ix_workshop_favorite_parts_part_id", "workshop_favorite_parts", ["part_id"], unique=False)

    op.create_table(
        "carts",
        sa.Column("status", sa.String(length=20), nullable=False, server_default="open"),
        sa.Column("created_by_user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("workshop_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["created_by_user_id"], ["users.id"], name="fk_carts_created_by_user_id_users"),
        sa.ForeignKeyConstraint(["workshop_id"], ["workshops.id"], name="fk_carts_workshop_id_workshops"),
    )
    op.create_index("ix_carts_workshop_id", "carts", ["workshop_id"], unique=False)
    op.create_index("ix_carts_created_by_user_id", "carts", ["created_by_user_id"], unique=False)

    op.create_table(
        "cart_items",
        sa.Column("cart_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("part_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("qty", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("chosen_supplier_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("unit_price_snapshot", sa.Numeric(precision=12, scale=2), nullable=False, server_default="0"),
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["cart_id"], ["carts.id"], name="fk_cart_items_cart_id_carts"),
        sa.ForeignKeyConstraint(["chosen_supplier_id"], ["suppliers.id"], name="fk_cart_items_chosen_supplier_id_suppliers"),
        sa.ForeignKeyConstraint(["part_id"], ["parts.id"], name="fk_cart_items_part_id_parts"),
        sa.UniqueConstraint("cart_id", "part_id", name="uq_cart_items_cart_part"),
    )
    op.create_index("ix_cart_items_cart_id", "cart_items", ["cart_id"], unique=False)
    op.create_index("ix_cart_items_part_id", "cart_items", ["part_id"], unique=False)
    op.create_index("ix_cart_items_chosen_supplier_id", "cart_items", ["chosen_supplier_id"], unique=False)

    op.create_table(
        "purchase_orders",
        sa.Column("order_number", sa.String(length=20), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="draft"),
        sa.Column("supplier_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("subtotal", sa.Numeric(precision=12, scale=2), nullable=False, server_default="0"),
        sa.Column("shipping", sa.Numeric(precision=12, scale=2), nullable=False, server_default="0"),
        sa.Column("discount", sa.Numeric(precision=12, scale=2), nullable=False, server_default="0"),
        sa.Column("total", sa.Numeric(precision=12, scale=2), nullable=False, server_default="0"),
        sa.Column("delivery_mode", sa.String(length=20), nullable=False, server_default="delivery"),
        sa.Column("delivery_address", sa.Text(), nullable=True),
        sa.Column("created_by_user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("workshop_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["created_by_user_id"], ["users.id"], name="fk_purchase_orders_created_by_user_id_users"),
        sa.ForeignKeyConstraint(["supplier_id"], ["suppliers.id"], name="fk_purchase_orders_supplier_id_suppliers"),
        sa.ForeignKeyConstraint(["workshop_id"], ["workshops.id"], name="fk_purchase_orders_workshop_id_workshops"),
        sa.UniqueConstraint("workshop_id", "order_number", name="uq_purchase_orders_workshop_order_number"),
    )
    op.create_index("ix_purchase_orders_workshop_id", "purchase_orders", ["workshop_id"], unique=False)
    op.create_index("ix_purchase_orders_supplier_id", "purchase_orders", ["supplier_id"], unique=False)
    op.create_index("ix_purchase_orders_created_by_user_id", "purchase_orders", ["created_by_user_id"], unique=False)

    op.create_table(
        "purchase_order_items",
        sa.Column("purchase_order_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("part_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("qty", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("unit_price", sa.Numeric(precision=12, scale=2), nullable=False, server_default="0"),
        sa.Column("total_price", sa.Numeric(precision=12, scale=2), nullable=False, server_default="0"),
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["part_id"], ["parts.id"], name="fk_purchase_order_items_part_id_parts"),
        sa.ForeignKeyConstraint(["purchase_order_id"], ["purchase_orders.id"], name="fk_purchase_order_items_purchase_order_id_purchase_orders"),
        sa.UniqueConstraint("purchase_order_id", "part_id", name="uq_purchase_order_items_po_part"),
    )
    op.create_index("ix_purchase_order_items_purchase_order_id", "purchase_order_items", ["purchase_order_id"], unique=False)
    op.create_index("ix_purchase_order_items_part_id", "purchase_order_items", ["part_id"], unique=False)

    op.create_table(
        "marketplace_settings",
        sa.Column("workshop_id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("allow_attendant_purchase", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("default_markup_percent", sa.Integer(), nullable=False, server_default="20"),
        sa.Column("pricing_mode", sa.String(length=20), nullable=False, server_default="markup"),
        sa.Column("pro_feature_enabled", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["workshop_id"], ["workshops.id"], name="fk_marketplace_settings_workshop_id_workshops"),
    )
    op.create_index("ix_marketplace_settings_workshop_id", "marketplace_settings", ["workshop_id"], unique=False)

    op.create_table(
        "commission_rules",
        sa.Column("mode", sa.String(length=20), nullable=False, server_default="percent"),
        sa.Column("value", sa.Numeric(precision=12, scale=2), nullable=False, server_default="0"),
        sa.Column("applies_to", sa.String(length=20), nullable=False, server_default="all"),
        sa.Column("category", sa.String(length=80), nullable=True),
        sa.Column("supplier_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("workshop_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["supplier_id"], ["suppliers.id"], name="fk_commission_rules_supplier_id_suppliers"),
        sa.ForeignKeyConstraint(["workshop_id"], ["workshops.id"], name="fk_commission_rules_workshop_id_workshops"),
    )
    op.create_index("ix_commission_rules_workshop_id", "commission_rules", ["workshop_id"], unique=False)
    op.create_index("ix_commission_rules_supplier_id", "commission_rules", ["supplier_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_commission_rules_supplier_id", table_name="commission_rules")
    op.drop_index("ix_commission_rules_workshop_id", table_name="commission_rules")
    op.drop_table("commission_rules")

    op.drop_index("ix_marketplace_settings_workshop_id", table_name="marketplace_settings")
    op.drop_table("marketplace_settings")

    op.drop_index("ix_purchase_order_items_part_id", table_name="purchase_order_items")
    op.drop_index("ix_purchase_order_items_purchase_order_id", table_name="purchase_order_items")
    op.drop_table("purchase_order_items")

    op.drop_index("ix_purchase_orders_created_by_user_id", table_name="purchase_orders")
    op.drop_index("ix_purchase_orders_supplier_id", table_name="purchase_orders")
    op.drop_index("ix_purchase_orders_workshop_id", table_name="purchase_orders")
    op.drop_table("purchase_orders")

    op.drop_index("ix_cart_items_chosen_supplier_id", table_name="cart_items")
    op.drop_index("ix_cart_items_part_id", table_name="cart_items")
    op.drop_index("ix_cart_items_cart_id", table_name="cart_items")
    op.drop_table("cart_items")

    op.drop_index("ix_carts_created_by_user_id", table_name="carts")
    op.drop_index("ix_carts_workshop_id", table_name="carts")
    op.drop_table("carts")

    op.drop_index("ix_workshop_favorite_parts_part_id", table_name="workshop_favorite_parts")
    op.drop_index("ix_workshop_favorite_parts_workshop_id", table_name="workshop_favorite_parts")
    op.drop_table("workshop_favorite_parts")

    op.drop_index("ix_supplier_parts_part_id", table_name="supplier_parts")
    op.drop_index("ix_supplier_parts_supplier_id", table_name="supplier_parts")
    op.drop_table("supplier_parts")

    op.drop_index("ix_workshop_suppliers_supplier_id", table_name="workshop_suppliers")
    op.drop_index("ix_workshop_suppliers_workshop_id", table_name="workshop_suppliers")
    op.drop_table("workshop_suppliers")

    op.drop_index("ix_subscriptions_workshop_id", table_name="subscriptions")
    op.drop_index("ix_subscriptions_kiwify_transaction_id", table_name="subscriptions")
    op.drop_table("subscriptions")

    op.drop_index("ix_payments_service_id", table_name="payments")
    op.drop_index("ix_payments_workshop_id", table_name="payments")
    op.drop_table("payments")

    op.drop_index("ix_returns_service_id", table_name="returns")
    op.drop_index("ix_returns_vehicle_id", table_name="returns")
    op.drop_index("ix_returns_customer_id", table_name="returns")
    op.drop_index("ix_returns_workshop_id", table_name="returns")
    op.drop_table("returns")

    op.drop_index("ix_return_rules_workshop_id", table_name="return_rules")
    op.drop_table("return_rules")

    op.drop_index("ix_quotes_service_id", table_name="quotes")
    op.drop_index("ix_quotes_workshop_id", table_name="quotes")
    op.drop_table("quotes")

    op.drop_index("ix_service_items_part_id", table_name="service_items")
    op.drop_index("ix_service_items_service_id", table_name="service_items")
    op.drop_index("ix_service_items_workshop_id", table_name="service_items")
    op.drop_table("service_items")

    op.drop_index("ix_services_created_by_user_id", table_name="services")
    op.drop_index("ix_services_customer_id", table_name="services")
    op.drop_index("ix_services_vehicle_id", table_name="services")
    op.drop_index("ix_services_workshop_id", table_name="services")
    op.drop_table("services")

    op.drop_index("ix_vehicles_customer_id", table_name="vehicles")
    op.drop_index("ix_vehicles_workshop_id", table_name="vehicles")
    op.drop_table("vehicles")

    op.drop_index("ix_customers_workshop_id", table_name="customers")
    op.drop_table("customers")

    op.drop_index("ix_refresh_tokens_user_id", table_name="refresh_tokens")
    op.drop_index("ix_refresh_tokens_workshop_id", table_name="refresh_tokens")
    op.drop_table("refresh_tokens")

    op.drop_index("ix_users_workshop_id", table_name="users")
    op.drop_table("users")

    op.drop_table("parts")
    op.drop_table("suppliers")
    op.drop_table("workshops")