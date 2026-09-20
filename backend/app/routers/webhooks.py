import datetime
from typing import Optional, Literal
from fastapi import APIRouter, Depends, status
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.orm import Session

try:
    from backend.app import models
    from backend.app.database import get_db
    from backend.app.routers.tickets import generate_ticket_id
    from backend.ai_engine.triage_agent import TriageAgent
except ImportError:
    from app import models
    from app.database import get_db
    from app.routers.tickets import generate_ticket_id
    from ai_engine.triage_agent import TriageAgent

router = APIRouter(prefix="/api/webhooks", tags=["System Design - Multi-Channel Webhooks"])


class InboundWebhookPayload(BaseModel):
    channel: Literal["WhatsApp", "Email", "Shopify", "Web Form"] = Field(
        ..., description="Inbound communication channel (e.g. WhatsApp, Email, Shopify)"
    )
    client_name: Optional[str] = Field("Aura D2C", description="Client brand identifier for multi-tenancy")
    customer_name: str = Field(..., min_length=2, description="Customer name")
    customer_email: EmailStr = Field(..., description="Customer contact email")
    subject: str = Field(..., min_length=2, description="Subject / Short description")
    description: str = Field(..., min_length=5, description="Full message payload")


class InboundWebhookResponse(BaseModel):
    status: str
    ticket_id: str
    channel: str
    client_name: str
    priority: str
    category: str
    ai_summary: Optional[str]
    created_at: datetime.datetime


@router.post(
    "/inbound",
    response_model=InboundWebhookResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Multi-Channel Webhook Ingestion Pipeline (WhatsApp / Shopify / Email / n8n)",
)
def ingest_webhook_ticket(
    payload: InboundWebhookPayload,
    db: Session = Depends(get_db),
):
    """
    Simulates high-throughput multi-channel ingestion for external platforms:
    - Accepts webhooks from WhatsApp Business API, Shopify Order Events, Email Parsers, or n8n
    - Auto-generates sequential ticket ID
    - Executes autonomous AI Triage via Groq Cloud
    - Indexes ticket under appropriate client brand
    """
    ticket_id = generate_ticket_id(db)
    now = datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None)

    # Autonomous AI triage powered by Groq
    triage = TriageAgent.analyze_ticket(
        subject=payload.subject.strip(),
        description=payload.description.strip(),
        customer_name=payload.customer_name.strip(),
        client_name=payload.client_name or "Aura D2C",
    )

    new_ticket = models.Ticket(
        ticket_id=ticket_id,
        customer_name=payload.customer_name.strip(),
        customer_email=payload.customer_email.strip().lower(),
        subject=payload.subject.strip(),
        description=payload.description.strip(),
        status="Open",
        priority=triage["priority"],
        category=triage["category"],
        channel=payload.channel,
        client_name=payload.client_name or "Aura D2C",
        ai_summary=triage["ai_summary"],
        created_at=now,
        updated_at=now,
    )

    db.add(new_ticket)
    db.commit()
    db.refresh(new_ticket)

    return InboundWebhookResponse(
        status="processed",
        ticket_id=new_ticket.ticket_id,
        channel=new_ticket.channel,
        client_name=new_ticket.client_name,
        priority=new_ticket.priority,
        category=new_ticket.category,
        ai_summary=new_ticket.ai_summary,
        created_at=new_ticket.created_at,
    )
