from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

try:
    from backend.app import models, schemas
    from backend.app.database import get_db
except ImportError:
    from app import models, schemas
    from app.database import get_db

router = APIRouter(prefix="/api/analytics", tags=["Analytics"])


@router.get("/metrics", response_model=schemas.AnalyticsMetrics, summary="Support team KPI metrics")
def get_metrics(db: Session = Depends(get_db)):
    """
    Computes high-level support operations KPIs:
    - Status breakdown (Open, In Progress, Closed)
    - Urgent tickets count
    - Resolution rate
    - Channel, Category, Priority, and Multi-client distribution
    """
    total = db.query(models.Ticket).count()
    open_cnt = db.query(models.Ticket).filter(models.Ticket.status == "Open").count()
    prog_cnt = db.query(models.Ticket).filter(models.Ticket.status == "In Progress").count()
    closed_cnt = db.query(models.Ticket).filter(models.Ticket.status == "Closed").count()
    urgent_cnt = db.query(models.Ticket).filter(models.Ticket.priority == "Urgent").count()

    resolution_rate = round((closed_cnt / total * 100), 1) if total > 0 else 0.0

    # Groupings
    def get_group_counts(column):
        results = db.query(column, func.count(models.Ticket.id)).group_by(column).all()
        return {str(val or "Unknown"): count for val, count in results}

    by_category = get_group_counts(models.Ticket.category)
    by_channel = get_group_counts(models.Ticket.channel)
    by_priority = get_group_counts(models.Ticket.priority)
    by_client = get_group_counts(models.Ticket.client_name)

    return schemas.AnalyticsMetrics(
        total_tickets=total,
        open_tickets=open_cnt,
        in_progress_tickets=prog_cnt,
        closed_tickets=closed_cnt,
        urgent_tickets=urgent_cnt,
        resolution_rate_percent=resolution_rate,
        by_category=by_category,
        by_channel=by_channel,
        by_priority=by_priority,
        by_client=by_client,
    )
