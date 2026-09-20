import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.app.main import app
from backend.app.database import Base, get_db

# Isolated in-memory SQLite database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session():
    """Create fresh database tables for each test function."""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    """FastAPI TestClient using the isolated database session."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def test_health_endpoints(client):
    """Verify system health and status endpoints."""
    res = client.get("/")
    assert res.status_code == 200
    assert res.json()["status"] == "online"

    res_health = client.get("/api/health")
    assert res_health.status_code == 200
    assert res_health.json()["status"] == "healthy"


def test_create_ticket_with_ai_auto_triage(client):
    """Verify POST /api/tickets creates a ticket and auto-triages urgency and category."""
    # An urgent damaged goods ticket
    payload = {
        "customer_name": "Rohan Gupta",
        "customer_email": "rohan.gupta@example.com",
        "subject": "Ceramic teapot broken into pieces",
        "description": "I opened package DS-8812 and the ceramic teapot is shattered and damaged.",
        "channel": "WhatsApp",
        "client_name": "UrbanKicks",
    }
    response = client.post("/api/tickets", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["ticket_id"].startswith("TKT-")
    assert data["priority"] == "Urgent"
    assert data["category"] == "Damaged Item"
    assert data["channel"] == "WhatsApp"
    assert data["client_name"] == "UrbanKicks"


def test_create_ticket_validation_errors(client):
    """Verify POST /api/tickets rejects invalid email or missing fields."""
    invalid_email_payload = {
        "customer_name": "Rohan",
        "customer_email": "not-an-email",
        "subject": "Test subject",
        "description": "Valid description long enough",
    }
    response = client.post("/api/tickets", json=invalid_email_payload)
    assert response.status_code == 422


def test_list_and_filter_tickets(client):
    """Verify GET /api/tickets list, status filtering, priority filtering, and search."""
    # Create two tickets
    client.post(
        "/api/tickets",
        json={
            "customer_name": "Aarav Mehta",
            "customer_email": "aarav@domain.com",
            "subject": "Order tracking issue",
            "description": "Where is my item tracking link?",
            "client_name": "Aura D2C",
        },
    )
    t2 = client.post(
        "/api/tickets",
        json={
            "customer_name": "Diya Sen",
            "customer_email": "diya@domain.com",
            "subject": "Refund requested for shoes",
            "description": "Shoes do not fit my size.",
            "client_name": "GlowCare",
        },
    ).json()

    # Update second ticket status
    client.put(f"/api/tickets/{t2['ticket_id']}", json={"status": "In Progress"})

    # 1. List all
    res_all = client.get("/api/tickets")
    assert res_all.status_code == 200
    assert len(res_all.json()) == 2

    # 2. Filter by status Open
    res_open = client.get("/api/tickets?status=Open")
    assert res_open.status_code == 200
    assert len(res_open.json()) == 1
    assert res_open.json()[0]["customer_name"] == "Aarav Mehta"

    # 3. Filter by client name
    res_client = client.get("/api/tickets?client=GlowCare")
    assert res_client.status_code == 200
    assert len(res_client.json()) == 1
    assert res_client.json()[0]["customer_name"] == "Diya Sen"

    # 4. Search by keyword
    res_kw = client.get("/api/tickets?search=tracking")
    assert res_kw.status_code == 200
    assert len(res_kw.json()) == 1
    assert res_kw.json()[0]["customer_name"] == "Aarav Mehta"

    # 5. Pagination
    res_page = client.get("/api/tickets?skip=0&limit=1")
    assert res_page.status_code == 200
    assert len(res_page.json()) == 1


def test_get_ticket_detail_and_notes(client):
    """Verify GET /api/tickets/{ticket_id} and PUT /api/tickets/{ticket_id} note updates."""
    create_res = client.post(
        "/api/tickets",
        json={
            "customer_name": "Tanvi Rao",
            "customer_email": "tanvi@rao.com",
            "subject": "Damaged perfume bottle",
            "description": "The bottle was leaked completely inside packaging.",
        },
    )
    ticket_id = create_res.json()["ticket_id"]

    detail_res = client.get(f"/api/tickets/{ticket_id}")
    assert detail_res.status_code == 200
    detail = detail_res.json()
    assert detail["ticket_id"] == ticket_id
    assert detail["status"] == "Open"
    assert detail["priority"] == "Urgent"
    assert detail["category"] == "Damaged Item"
    assert detail["ai_summary"] is not None

    # Add note and update status via PUT
    put_res = client.put(
        f"/api/tickets/{ticket_id}",
        json={
            "status": "In Progress",
            "notes": "Requested customer to share photos of leaked package.",
        },
    )
    assert put_res.status_code == 200
    assert put_res.json()["success"] is True

    # Verify updated detail
    updated_detail = client.get(f"/api/tickets/{ticket_id}").json()
    assert updated_detail["status"] == "In Progress"
    assert len(updated_detail["notes"]) == 1


def test_ai_triage_and_draft_endpoints(client):
    """Verify AI Triage and 1-Click AI Draft response endpoints."""
    create_res = client.post(
        "/api/tickets",
        json={
            "customer_name": "Siddharth Roy",
            "customer_email": "sid.roy@gmail.com",
            "subject": "Delayed shipment for Order #DS-9901",
            "description": "Package is delayed for 5 days without any tracking movement.",
        },
    )
    ticket_id = create_res.json()["ticket_id"]

    # 1. Run AI Triage
    triage_res = client.post(f"/api/tickets/{ticket_id}/ai-triage")
    assert triage_res.status_code == 200
    triage_data = triage_res.json()
    assert triage_data["ticket_id"] == ticket_id
    assert triage_data["category"] == "Shipping & Delivery"
    assert "DS-9901" in triage_data["ai_summary"]
    assert "Siddharth" in triage_data["suggested_reply"]

    # 2. Run AI Draft
    draft_res = client.post(f"/api/tickets/{ticket_id}/ai-draft")
    assert draft_res.status_code == 200
    draft_data = draft_res.json()
    reply = draft_data["suggested_reply"].replace("\u2011", "-")
    assert "DS-9901" in reply or "9901" in reply


def test_order_context_simulation(client):
    """Verify simulated D2C e-commerce order context lookup."""
    create_res = client.post(
        "/api/tickets",
        json={
            "customer_name": "Priya Sharma",
            "customer_email": "priya.sharma@example.com",
            "subject": "Order update needed",
            "description": "When will my package arrive?",
        },
    )
    ticket_id = create_res.json()["ticket_id"]

    order_res = client.get(f"/api/tickets/{ticket_id}/order-context")
    assert order_res.status_code == 200
    order_data = order_res.json()
    assert order_data["order_id"] == "DS-9901"
    assert "BlueDart" in order_data["carrier"]
    assert len(order_data["items"]) > 0


def test_analytics_metrics(client):
    """Verify GET /api/analytics/metrics computes correct counts and distributions."""
    client.post(
        "/api/tickets",
        json={
            "customer_name": "Alice",
            "customer_email": "alice@example.com",
            "subject": "Double charged via UPI",
            "description": "Payment was deducted twice.",
            "channel": "WhatsApp",
            "client_name": "Aura D2C",
        },
    )

    res = client.get("/api/analytics/metrics")
    assert res.status_code == 200
    metrics = res.json()
    assert metrics["total_tickets"] == 1
    assert metrics["open_tickets"] == 1
    assert metrics["urgent_tickets"] == 1
    assert "WhatsApp" in metrics["by_channel"]
    assert "Aura D2C" in metrics["by_client"]


def test_webhook_inbound_ingestion(client):
    """Verify POST /api/webhooks/inbound ingests multi-channel events with auto AI triage."""
    webhook_payload = {
        "channel": "WhatsApp",
        "client_name": "UrbanKicks",
        "customer_name": "Kavita Nair",
        "customer_email": "kavita.nair@gmail.com",
        "subject": "Exchange request for Order #DS-8812",
        "description": "Heels size is too tight. Need size 7 instead of size 6.",
    }
    response = client.post("/api/webhooks/inbound", json=webhook_payload)
    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "processed"
    assert data["ticket_id"].startswith("TKT-")
    assert data["channel"] == "WhatsApp"
    assert data["client_name"] == "UrbanKicks"
    assert data["category"] in ["Refund / Return", "Order Modification"]
    assert data["ai_summary"] is not None
