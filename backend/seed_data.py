import sys
import os
from datetime import datetime, timedelta, timezone

# Ensure project root is in path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.app.database import SessionLocal, engine, Base
from backend.app import models
from backend.app.main import auto_migrate_schema


def seed_database():
    """Populates the database with realistic D2C customer support tickets, AI triage, and notes."""
    print("Ensuring tables and columns exist...")
    auto_migrate_schema()

    db = SessionLocal()
    try:
        existing_count = db.query(models.Ticket).count()
        if existing_count > 0:
            print(f"Clearing {existing_count} existing tickets for a fresh seed...")
            db.query(models.Note).delete()
            db.query(models.Ticket).delete()
            db.commit()

        sample_tickets = [
            {
                "ticket_id": "TKT-101",
                "customer_name": "Priya Sharma",
                "customer_email": "priya.sharma@example.com",
                "subject": "Delayed delivery for Order #DS-9901",
                "description": "I ordered the herbal hair care combo 5 days ago with express shipping, but the tracking status is stuck at 'Arrived at Sorting Hub Mumbai'. Please update on when it will arrive.",
                "status": "Open",
                "priority": "High",
                "category": "Shipping & Delivery",
                "channel": "WhatsApp",
                "client_name": "Aura D2C",
                "ai_summary": "Shipment #DS-9901 delayed at Mumbai Hub; customer requested tracking update for urgent order.",
                "minutes_ago": 180,
                "notes": [
                    "Escalated to logistics dispatch team. Waiting for BlueDart AWB scan.",
                ],
            },
            {
                "ticket_id": "TKT-102",
                "customer_name": "Rahul Verma",
                "customer_email": "rahul.v@gmail.com",
                "subject": "Received damaged ceramic coffee mug set",
                "description": "Unboxed package #DS-9844 today. Two out of four mugs are cracked into pieces due to poor bubble wrap packaging. Requesting an immediate replacement or full refund.",
                "status": "In Progress",
                "priority": "Urgent",
                "category": "Damaged Item",
                "channel": "Email",
                "client_name": "UrbanKicks",
                "ai_summary": "Customer reported 2 ceramic mugs broken in transit (#DS-9844); requested expedited replacement or refund.",
                "minutes_ago": 360,
                "notes": [
                    "Customer provided unboxing photos via email. Verified damage.",
                    "Initiated return pick-up and issued reverse logistics ticket #RL-402.",
                ],
            },
            {
                "ticket_id": "TKT-103",
                "customer_name": "Aanya Kapoor",
                "customer_email": "aanya.k@outlook.com",
                "subject": "Wrong item delivered in Order #DS-9780",
                "description": "I ordered a Lavender Essential Oil 30ml, but received Citrus Orange Body Wash instead. Please arrange exchange asap as this was a gift.",
                "status": "In Progress",
                "priority": "High",
                "category": "Refund / Return",
                "channel": "Shopify",
                "client_name": "GlowCare",
                "ai_summary": "Wrong item dispatch error (#DS-9780); customer received body wash instead of essential oil.",
                "minutes_ago": 720,
                "notes": [
                    "Warehouse packing error confirmed.",
                    "Correct item dispatched under expedited shipping AWB 77219904.",
                ],
            },
            {
                "ticket_id": "TKT-104",
                "customer_name": "Vikram Malhotra",
                "customer_email": "vikram.m@techcorp.in",
                "subject": "Payment deducted twice via UPI",
                "description": "During checkout, the UPI transaction failed first time but Rs. 2,499 was debited twice from my HDFC account (UPI Ref: 4099238812). Only one order was confirmed.",
                "status": "Closed",
                "priority": "Urgent",
                "category": "Billing & Payment",
                "channel": "Web Form",
                "client_name": "Aura D2C",
                "ai_summary": "Duplicate UPI payment deduction of ₹2,499; verified and resolved with gateway refund ARN.",
                "minutes_ago": 1440,
                "notes": [
                    "Razorpay payment gateway log checked. Duplicate authorization found.",
                    "Refund ARN 9931828192 issued. Settled back to customer's account in 24 hours.",
                ],
            },
            {
                "ticket_id": "TKT-105",
                "customer_name": "Sneha Patel",
                "customer_email": "sneha.patel@yahoo.com",
                "subject": "Discount coupon 'SUMMER20' not applying at checkout",
                "description": "I have items worth Rs. 1,800 in my cart, but the coupon code gives an 'invalid code' error even though your Instagram story states it is valid today.",
                "status": "Closed",
                "priority": "Normal",
                "category": "Promotions & Discounts",
                "channel": "WhatsApp",
                "client_name": "UrbanKicks",
                "ai_summary": "Coupon SUMMER20 min-spend threshold query; customer assisted with discount voucher.",
                "minutes_ago": 2880,
                "notes": [
                    "Coupon min-order condition was Rs. 2,000. Informed customer and provided an exclusive Rs. 200 concession voucher.",
                ],
            },
            {
                "ticket_id": "TKT-106",
                "customer_name": "Karan Singhania",
                "customer_email": "karan.singh@gmail.com",
                "subject": "Need invoice with GSTIN for business purchase",
                "description": "I placed order #DS-9650 for my office supplies and entered my company GSTIN 27AABCU9603R1ZM, but received a standard B2C invoice without tax credits.",
                "status": "Open",
                "priority": "Medium",
                "category": "Billing & Payment",
                "channel": "Email",
                "client_name": "Aura D2C",
                "ai_summary": "Request for corrected B2B tax invoice with GSTIN 27AABCU9603R1ZM for order #DS-9650.",
                "minutes_ago": 90,
                "notes": [],
            },
            {
                "ticket_id": "TKT-107",
                "customer_name": "Ananya Joshi",
                "customer_email": "ananya.j@gmail.com",
                "subject": "Address modification request before shipment",
                "description": "I just placed order #DS-10022 ten minutes ago. I accidentally selected my old home address. Please change delivery address to Flat 402, Green Glen, Mumbai 400076.",
                "status": "In Progress",
                "priority": "High",
                "category": "Order Modification",
                "channel": "Shopify",
                "client_name": "GlowCare",
                "ai_summary": "Pre-dispatch address change request for newly placed order #DS-10022.",
                "minutes_ago": 45,
                "notes": [
                    "Order placed on hold in Shopify backend before label generation.",
                ],
            },
        ]

        now = datetime.now(timezone.utc).replace(tzinfo=None)

        for item in sample_tickets:
            created_time = now - timedelta(minutes=item["minutes_ago"])
            ticket = models.Ticket(
                ticket_id=item["ticket_id"],
                customer_name=item["customer_name"],
                customer_email=item["customer_email"],
                subject=item["subject"],
                description=item["description"],
                status=item["status"],
                priority=item["priority"],
                category=item["category"],
                channel=item["channel"],
                client_name=item["client_name"],
                ai_summary=item["ai_summary"],
                created_at=created_time,
                updated_at=created_time + timedelta(minutes=15) if item["notes"] else created_time,
            )
            db.add(ticket)
            db.flush()

            for note_text in item["notes"]:
                note = models.Note(
                    ticket_id=ticket.ticket_id,
                    note_text=note_text,
                    created_at=created_time + timedelta(minutes=20),
                )
                db.add(note)

        db.commit()
        print(f"Successfully seeded {len(sample_tickets)} realistic multi-channel, AI-triaged D2C tickets!")

    except Exception as e:
        db.rollback()
        print(f"Error seeding database: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
