import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
try:
    from backend.app.database import Base
except ImportError:
    from app.database import Base


def get_utc_now():
    return datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None)


class Ticket(Base):
    __tablename__ = "tickets"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    ticket_id = Column(String(50), unique=True, index=True, nullable=False)
    customer_name = Column(String(255), nullable=False, index=True)
    customer_email = Column(String(255), nullable=False, index=True)
    subject = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    status = Column(String(50), default="Open", nullable=False, index=True)
    priority = Column(String(50), default="Normal", nullable=False, index=True)  # Urgent, High, Medium, Normal
    category = Column(String(100), default="General", nullable=False, index=True)  # Shipping, Damaged, Refund, Billing, General
    channel = Column(String(50), default="Web Form", nullable=False, index=True)  # Email, WhatsApp, Web Form, Shopify
    client_name = Column(String(100), default="Aura D2C", nullable=False, index=True)  # Multi-client / brand tag
    ai_summary = Column(Text, nullable=True)  # 1-sentence AI executive summary
    created_at = Column(DateTime, default=get_utc_now, nullable=False, index=True)
    updated_at = Column(
        DateTime,
        default=get_utc_now,
        onupdate=get_utc_now,
        nullable=False,
    )

    # Relationships
    notes = relationship(
        "Note",
        back_populates="ticket",
        cascade="all, delete-orphan",
        order_by="Note.created_at.asc()",
    )


class Note(Base):
    __tablename__ = "notes"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    ticket_id = Column(String(50), ForeignKey("tickets.ticket_id", ondelete="CASCADE"), nullable=False, index=True)
    note_text = Column(Text, nullable=False)
    created_at = Column(DateTime, default=get_utc_now, nullable=False)

    # Relationships
    ticket = relationship("Ticket", back_populates="notes")
