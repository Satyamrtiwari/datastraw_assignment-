from datetime import datetime
from typing import List, Optional, Literal, Dict, Any
from pydantic import BaseModel, EmailStr, Field


class TicketCreate(BaseModel):
    customer_name: str = Field(..., min_length=2, max_length=255, description="Full name of customer")
    customer_email: EmailStr = Field(..., description="Valid email address of customer")
    subject: str = Field(..., min_length=2, max_length=255, description="Brief summary of issue")
    description: str = Field(..., min_length=5, description="Detailed problem description")
    channel: Optional[Literal["Web Form", "Email", "WhatsApp", "Shopify"]] = "Web Form"
    client_name: Optional[str] = "Aura D2C"
    priority: Optional[Literal["Urgent", "High", "Medium", "Normal"]] = "Normal"
    category: Optional[str] = "General"


class TicketCreateResponse(BaseModel):
    ticket_id: str
    created_at: datetime
    priority: Optional[str] = "Normal"
    category: Optional[str] = "General"
    channel: Optional[str] = "Web Form"
    client_name: Optional[str] = "Aura D2C"

    model_config = {"from_attributes": True}


class NoteResponse(BaseModel):
    id: int
    ticket_id: str
    note_text: str
    created_at: datetime

    model_config = {"from_attributes": True}


class TicketListItem(BaseModel):
    ticket_id: str
    customer_name: str
    customer_email: str
    subject: str
    status: str
    priority: str = "Normal"
    category: str = "General"
    channel: str = "Web Form"
    client_name: str = "Aura D2C"
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class TicketDetail(BaseModel):
    ticket_id: str
    customer_name: str
    customer_email: str
    subject: str
    description: str
    status: str
    priority: str = "Normal"
    category: str = "General"
    channel: str = "Web Form"
    client_name: str = "Aura D2C"
    ai_summary: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    notes: List[NoteResponse] = []

    model_config = {"from_attributes": True}


class TicketUpdate(BaseModel):
    status: Optional[Literal["Open", "In Progress", "Closed"]] = None
    priority: Optional[Literal["Urgent", "High", "Medium", "Normal"]] = None
    category: Optional[str] = None
    notes: Optional[str] = Field(None, description="Internal note/comment to attach to ticket")


class TicketUpdateResponse(BaseModel):
    success: bool
    updated_at: datetime
    ticket_id: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None


# AI Copilot Schemas
class AITriageResponse(BaseModel):
    ticket_id: str
    priority: str
    category: str
    ai_summary: str
    suggested_reply: str
    confidence_score: float = 0.94
    model: str


class AIDraftResponse(BaseModel):
    ticket_id: str
    customer_name: str
    suggested_reply: str
    model: str


# Simulated Order Schemas
class OrderItem(BaseModel):
    title: str
    qty: int
    price: str


class CustomerOrderContext(BaseModel):
    order_id: str
    order_date: str
    fulfillment_status: str
    carrier: str
    tracking_number: str
    tracking_url: str
    order_total: str
    items: List[OrderItem]
    shipping_address: str


# Support Team Analytics / KPI Schemas
class AnalyticsMetrics(BaseModel):
    total_tickets: int
    open_tickets: int
    in_progress_tickets: int
    closed_tickets: int
    urgent_tickets: int
    resolution_rate_percent: float
    by_category: Dict[str, int]
    by_channel: Dict[str, int]
    by_priority: Dict[str, int]
    by_client: Dict[str, int]
