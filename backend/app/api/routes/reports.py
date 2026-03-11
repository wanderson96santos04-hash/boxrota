from datetime import datetime

from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from app.db.deps import get_db
from app.core.auth import get_current_user
from app.models.user import User
from app.models.service import Service
from app.models.enums import ServiceStatus

router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("/month")
def reports_month(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    workshop_id = user.workshop_id
    now = datetime.utcnow()

    finished_statuses = [
        ServiceStatus.completed.value,
        ServiceStatus.delivered.value,
    ]

    revenue = (
        db.query(func.coalesce(func.sum(Service.total_amount), 0))
        .filter(
            Service.workshop_id == workshop_id,
            Service.status.in_(finished_statuses),
            func.extract("month", Service.created_at) == now.month,
            func.extract("year", Service.created_at) == now.year,
        )
        .scalar()
    )

    finished_orders = (
        db.query(func.count(Service.id))
        .filter(
            Service.workshop_id == workshop_id,
            Service.status.in_(finished_statuses),
            func.extract("month", Service.created_at) == now.month,
            func.extract("year", Service.created_at) == now.year,
        )
        .scalar()
    )

    open_value = (
        db.query(func.coalesce(func.sum(Service.total_amount), 0))
        .filter(
            Service.workshop_id == workshop_id,
            Service.status.in_(
                [
                    ServiceStatus.open.value,
                    ServiceStatus.in_progress.value,
                    ServiceStatus.waiting_parts.value,
                ]
            ),
            func.extract("month", Service.created_at) == now.month,
            func.extract("year", Service.created_at) == now.year,
        )
        .scalar()
    )

    average_ticket = 0
    if finished_orders and int(finished_orders) > 0:
        average_ticket = float(revenue or 0) / int(finished_orders)

    recent_services = (
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
        "revenue": float(revenue or 0),
        "open_value": float(open_value or 0),
        "finished_orders": int(finished_orders or 0),
        "average_ticket": float(average_ticket or 0),
        "recent_services": [
            {
                "id": str(s.id),
                "plate": s.vehicle.plate if s.vehicle else "",
                "customer_name": s.customer.name if s.customer else "",
                "total": float(s.total_amount or 0),
                "status": s.status,
                "created_at": s.created_at.isoformat() if s.created_at else None,
            }
            for s in recent_services
        ],
    }