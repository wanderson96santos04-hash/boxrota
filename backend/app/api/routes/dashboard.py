from datetime import datetime
from sqlalchemy import func
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session, joinedload

from app.db.deps import get_db
from app.core.auth import get_current_user
from app.models.user import User
from app.models.service import Service
from app.models.enums import ServiceStatus

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("")
def dashboard_stats(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    workshop_id = user.workshop_id

    # =========================
    # SERVIÇOS EM ANDAMENTO
    # =========================

    open_services = (
        db.query(func.count(Service.id))
        .filter(
            Service.workshop_id == workshop_id,
            Service.status.in_(
                [
                    ServiceStatus.open.value,
                    ServiceStatus.in_progress.value,
                    ServiceStatus.waiting_parts.value,
                ]
            ),
        )
        .scalar()
    )

    # =========================
    # FATURAMENTO DO MÊS
    # =========================

    now = datetime.utcnow()

    revenue_month = (
        db.query(func.coalesce(func.sum(Service.total_amount), 0))
        .filter(
            Service.workshop_id == workshop_id,
            Service.status.in_(
                [
                    ServiceStatus.completed.value,
                    ServiceStatus.delivered.value,
                ]
            ),
            func.extract("month", Service.created_at) == now.month,
            func.extract("year", Service.created_at) == now.year,
        )
        .scalar()
    )

    # =========================
    # ÚLTIMOS SERVIÇOS
    # =========================

    last_services = (
        db.query(Service)
        .options(
            joinedload(Service.vehicle),
            joinedload(Service.customer),
        )
        .filter(Service.workshop_id == workshop_id)
        .order_by(Service.created_at.desc())
        .limit(5)
        .all()
    )

    return {
        "open_services": open_services or 0,
        "revenue_month": float(revenue_month or 0),
        "last_services": [
            {
                "id": str(s.id),
                "plate": s.vehicle.plate if s.vehicle else "",
                "customer_name": s.customer.name if s.customer else "",
                "total": float(s.total_amount or 0),
                "status": s.status,
                "updated_at": s.updated_at.isoformat() if s.updated_at else None,
            }
            for s in last_services
        ],
    }