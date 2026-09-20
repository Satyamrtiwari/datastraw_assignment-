import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import or_
from sqlalchemy.orm import Session

try:
    from backend.app import models, schemas
    from backend.app.database import get_db
    from backend.app.services.order_service import OrderService
    from backend.ai_engine.triage_agent import TriageAgent
    from backend.ai_engine.draft_copilot import DraftCopilot
except ImportError:
    from app import models, schemas
    from app.database import get_db
    from app.services.order_service import OrderService
    from ai_engine.triage_agent import TriageAgent
    from ai_engine.draft_copilot import DraftCopilot

router = APIRouter(prefix="/api/tickets", tags=["Tickets"])


def generate_ticket_id(db: Session) -> str:
    """Generate a unique sequential human-readable ticket ID (e.g., TKT-101, TKT-102)."""
    last_ticket = db.query(models.Ticket).order_by(models.Ticket.id.desc()).first()
    if last_ticket and last_ticket.id:
        next_num = 100 + last_ticket.id + 1
    else:
        next_num = 101

    # Guarantee uniqueness even if custom IDs exist
    while db.query(models.Ticket).filter(models.Ticket.ticket_id == f"TKT-{next_num}").first():
        next_num += 1

    return f"TKT-{next_num}"


@router.post(
    "",
    response_model=schemas.TicketCreateResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new support ticket with automatic AI triage",
)
def create_ticket(
    ticket_in: schemas.TicketCreate,
    db: Session = Depends(get_db),
):
    """
    Creates a new support ticket with auto-generated unique ticket ID, timestamp,
    channel tag, multi-client brand tag, and intelligent auto-triage.
    """
    ticket_id = generate_ticket_id(db)
    now = datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None)

    # Perform intelligent AI triage via Groq
    ai_result = TriageAgent.analyze_ticket(
        subject=ticket_in.subject.strip(),
        description=ticket_in.description.strip(),
        customer_name=ticket_in.customer_name.strip(),
        client_name=ticket_in.client_name or "Aura D2C",
    )

    priority = ticket_in.priority if ticket_in.priority and ticket_in.priority != "Normal" else ai_result["priority"]
    category = ticket_in.category if ticket_in.category and ticket_in.category != "General" else ai_result["category"]

    new_ticket = models.Ticket(
        ticket_id=ticket_id,
        customer_name=ticket_in.customer_name.strip(),
        customer_email=ticket_in.customer_email.strip().lower(),
        subject=ticket_in.subject.strip(),
        description=ticket_in.description.strip(),
        status="Open",
        priority=priority,
        category=category,
        channel=ticket_in.channel or "Web Form",
        client_name=ticket_in.client_name or "Aura D2C",
        ai_summary=ai_result["ai_summary"],
        created_at=now,
        updated_at=now,
    )

    db.add(new_ticket)
    db.commit()
    db.refresh(new_ticket)

    return schemas.TicketCreateResponse(
        ticket_id=new_ticket.ticket_id,
        created_at=new_ticket.created_at,
        priority=new_ticket.priority,
        category=new_ticket.category,
        channel=new_ticket.channel,
        client_name=new_ticket.client_name,
    )


@router.post(
    "/seed",
    summary="Populate database with realistic multi-tenant demo tickets and notes",
)
def seed_demo_data():
    """
    Populate database with pre-configured realistic D2C tickets across multiple brands
    and channels with notes for testing and evaluator demonstration.
    """
    try:
        from backend.seed_data import seed_database
    except ImportError:
        from seed_data import seed_database
    seed_database()
    return {"success": True, "message": "Demo data populated successfully"}


@router.get(
    "",
    response_model=List[schemas.TicketListItem],
    summary="List all tickets with search, filtering, and pagination",
)
def list_tickets(
    status: Optional[str] = Query(None, description="Filter by status: Open, In Progress, Closed"),
    priority: Optional[str] = Query(None, description="Filter by priority: Urgent, High, Medium, Normal"),
    category: Optional[str] = Query(None, description="Filter by category"),
    channel: Optional[str] = Query(None, description="Filter by channel: Email, WhatsApp, Web Form, Shopify"),
    client: Optional[str] = Query(None, description="Filter by client brand"),
    search: Optional[str] = Query(None, description="Search across customer name, email, ticket ID, subject, or description"),
    skip: int = Query(0, ge=0, description="Pagination offset"),
    limit: int = Query(50, ge=1, le=200, description="Pagination limit"),
    db: Session = Depends(get_db),
):
    """
    Retrieve tickets filtered by status, priority, category, channel, client, or search keyword.
    Supports server-side pagination for scalable throughput.
    """
    query = db.query(models.Ticket)

    # Status filter
    if status and status.strip() and status != "All":
        query = query.filter(models.Ticket.status.ilike(status.strip()))

    # Priority filter
    if priority and priority.strip() and priority != "All":
        query = query.filter(models.Ticket.priority.ilike(priority.strip()))

    # Category filter
    if category and category.strip() and category != "All":
        query = query.filter(models.Ticket.category.ilike(category.strip()))

    # Channel filter
    if channel and channel.strip() and channel != "All":
        query = query.filter(models.Ticket.channel.ilike(channel.strip()))

    # Client / Multi-tenant filter
    if client and client.strip() and client != "All":
        query = query.filter(models.Ticket.client_name.ilike(f"%{client.strip()}%"))

    # Search filter across multiple fields
    if search and search.strip():
        term = f"%{search.strip()}%"
        query = query.filter(
            or_(
                models.Ticket.ticket_id.ilike(term),
                models.Ticket.customer_name.ilike(term),
                models.Ticket.customer_email.ilike(term),
                models.Ticket.subject.ilike(term),
                models.Ticket.description.ilike(term),
            )
        )

    # Sort newest first, apply pagination
    tickets = query.order_by(models.Ticket.created_at.desc()).offset(skip).limit(limit).all()
    return tickets


@router.get(
    "/{ticket_id}",
    response_model=schemas.TicketDetail,
    summary="Get detailed view of a ticket including internal notes",
)
def get_ticket(
    ticket_id: str,
    db: Session = Depends(get_db),
):
    """
    Retrieve ticket details and all associated notes by ticket_id.
    """
    ticket = (
        db.query(models.Ticket)
        .filter(models.Ticket.ticket_id == ticket_id.strip().upper())
        .first()
    )

    if not ticket:
        ticket = (
            db.query(models.Ticket)
            .filter(models.Ticket.ticket_id.ilike(ticket_id.strip()))
            .first()
        )

    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ticket with ID '{ticket_id}' not found",
        )

    return ticket


@router.put(
    "/{ticket_id}",
    response_model=schemas.TicketUpdateResponse,
    summary="Update ticket status, priority, category, and/or add internal notes",
)
def update_ticket(
    ticket_id: str,
    payload: schemas.TicketUpdate,
    db: Session = Depends(get_db),
):
    """
    Update ticket status, priority, category, and/or append internal collaboration note.
    """
    ticket = (
        db.query(models.Ticket)
        .filter(models.Ticket.ticket_id.ilike(ticket_id.strip()))
        .first()
    )

    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ticket with ID '{ticket_id}' not found",
        )

    now = datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None)
    updated = False

    # Update status
    if payload.status:
        ticket.status = payload.status
        updated = True

    # Update priority
    if payload.priority:
        ticket.priority = payload.priority
        updated = True

    # Update category
    if payload.category:
        ticket.category = payload.category
        updated = True

    # Add note
    if payload.notes and payload.notes.strip():
        new_note = models.Note(
            ticket_id=ticket.ticket_id,
            note_text=payload.notes.strip(),
            created_at=now,
        )
        db.add(new_note)
        updated = True

    if updated:
        ticket.updated_at = now
        db.commit()
        db.refresh(ticket)

    return schemas.TicketUpdateResponse(
        success=True,
        updated_at=ticket.updated_at,
        ticket_id=ticket.ticket_id,
        status=ticket.status,
        priority=ticket.priority,
    )


# ==========================================
# 🌟 UNIQUE AI & D2C STANDOUT ENDPOINTS
# ==========================================

@router.post(
    "/{ticket_id}/ai-triage",
    response_model=schemas.AITriageResponse,
    summary="Re-analyze ticket with AI Copilot for sentiment, urgency, category, and summary",
)
def run_ai_triage(
    ticket_id: str,
    db: Session = Depends(get_db),
):
    """
    Re-runs AI analysis on an existing ticket, updates the database record with
    discovered priority, category, and summary, and returns suggested action.
    """
    ticket = (
        db.query(models.Ticket)
        .filter(models.Ticket.ticket_id.ilike(ticket_id.strip()))
        .first()
    )

    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ticket with ID '{ticket_id}' not found",
        )

    result = TriageAgent.analyze_ticket(
        subject=ticket.subject,
        description=ticket.description,
        customer_name=ticket.customer_name,
        client_name=ticket.client_name,
    )

    # Persist updated triage
    ticket.priority = result["priority"]
    ticket.category = result["category"]
    ticket.ai_summary = result["ai_summary"]
    ticket.updated_at = datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None)
    db.commit()

    return schemas.AITriageResponse(
        ticket_id=ticket.ticket_id,
        priority=ticket.priority,
        category=ticket.category,
        ai_summary=ticket.ai_summary,
        suggested_reply=result["suggested_reply"],
        confidence_score=result["confidence_score"],
        model=result["model"],
    )


@router.post(
    "/{ticket_id}/ai-draft",
    response_model=schemas.AIDraftResponse,
    summary="Generate 1-click AI draft reply for support agent via Groq",
)
def generate_ai_draft(
    ticket_id: str,
    db: Session = Depends(get_db),
):
    """
    Generates a personalized, context-aware resolution response for the ticket
    utilizing Groq Cloud, live order context, and internal collaboration notes.
    """
    ticket = (
        db.query(models.Ticket)
        .filter(models.Ticket.ticket_id.ilike(ticket_id.strip()))
        .first()
    )

    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ticket with ID '{ticket_id}' not found",
        )

    # Fetch order context and notes history to feed into Groq copilot
    order_context = OrderService.get_order_context(
        customer_email=ticket.customer_email,
        text_content=f"{ticket.subject} {ticket.description}",
    )
    notes_history = [n.note_text for n in ticket.notes]

    result = DraftCopilot.generate_draft(
        subject=ticket.subject,
        description=ticket.description,
        customer_name=ticket.customer_name,
        client_name=ticket.client_name,
        notes_history=notes_history,
        order_context=order_context,
    )

    return schemas.AIDraftResponse(
        ticket_id=ticket.ticket_id,
        customer_name=ticket.customer_name,
        suggested_reply=result["suggested_reply"],
        model=result["model"],
    )


@router.get(
    "/{ticket_id}/order-context",
    response_model=schemas.CustomerOrderContext,
    summary="Fetch simulated D2C e-commerce order context for the customer",
)
def get_order_context(
    ticket_id: str,
    db: Session = Depends(get_db),
):
    """
    Simulates real-time Shopify / D2C e-commerce order lookup matching the customer's email or order ID.
    Provides courier, tracking link, order items, and shipping status to support agents.
    """
    ticket = (
        db.query(models.Ticket)
        .filter(models.Ticket.ticket_id.ilike(ticket_id.strip()))
        .first()
    )

    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ticket with ID '{ticket_id}' not found",
        )

    context = OrderService.get_order_context(
        customer_email=ticket.customer_email,
        text_content=f"{ticket.subject} {ticket.description}",
    )

    return context
