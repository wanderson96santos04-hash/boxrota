import enum


# =========================
# USER
# =========================

class UserRole(str, enum.Enum):
    admin = "admin"
    attendant = "attendant"


# =========================
# SERVICE / OS
# =========================

class ServiceStatus(str, enum.Enum):
    draft = "draft"
    open = "open"
    in_progress = "in_progress"
    waiting_parts = "waiting_parts"
    completed = "completed"
    delivered = "delivered"
    canceled = "canceled"


# =========================
# QUOTES
# =========================

class QuoteStatus(str, enum.Enum):
    draft = "draft"
    sent = "sent"
    approved = "approved"
    rejected = "rejected"
    expired = "expired"


# =========================
# RETURNS
# =========================

class ReturnStatus(str, enum.Enum):
    pending = "pending"
    approved = "approved"
    rejected = "rejected"


# =========================
# MARKETPLACE
# =========================

class AvailabilityStatus(str, enum.Enum):
    in_stock = "in_stock"
    low = "low"
    out = "out"
    unknown = "unknown"


class CartStatus(str, enum.Enum):
    open = "open"
    ordered = "ordered"
    abandoned = "abandoned"


class DeliveryMode(str, enum.Enum):
    delivery = "delivery"
    pickup = "pickup"


class PricingMode(str, enum.Enum):
    markup = "markup"
    manual = "manual"


class PurchaseOrderStatus(str, enum.Enum):
    draft = "draft"
    placed = "placed"
    confirmed = "confirmed"
    shipped = "shipped"
    delivered = "delivered"
    canceled = "canceled"


class CommissionMode(str, enum.Enum):
    percent = "percent"
    fixed = "fixed"


class CommissionAppliesTo(str, enum.Enum):
    all = "all"
    category = "category"
    supplier = "supplier"


# =========================
# SUBSCRIPTION
# =========================

class SubscriptionPlan(str, enum.Enum):
    basic = "basic"
    pro = "pro"


class SubscriptionStatus(str, enum.Enum):
    active = "active"
    canceled = "canceled"
    expired = "expired"