import re
from typing import Dict, Any, Optional, List


# Pre-mapped realistic D2C simulated orders
MOCK_ORDERS: Dict[str, Dict[str, Any]] = {
    "priya.sharma@example.com": {
        "order_id": "DS-9901",
        "order_date": "2026-09-15",
        "fulfillment_status": "In Transit",
        "carrier": "BlueDart Express",
        "tracking_number": "BD-772189021",
        "tracking_url": "https://track.bluedart.com/?awb=BD-772189021",
        "order_total": "₹1,850.00",
        "items": [
            {"title": "Herbal Hair Care Combo (Shampoo + Oil)", "qty": 1, "price": "₹1,450.00"},
            {"title": "Bamboo Scalp Massager", "qty": 1, "price": "₹400.00"},
        ],
        "shipping_address": "Bandra West, Mumbai, MH 400050",
    },
    "rahul.v@gmail.com": {
        "order_id": "DS-9844",
        "order_date": "2026-09-17",
        "fulfillment_status": "Delivered",
        "carrier": "Delhivery",
        "tracking_number": "DEL-90812398",
        "tracking_url": "https://delhivery.com/track?pin=DEL-90812398",
        "order_total": "₹2,199.00",
        "items": [
            {"title": "Handcrafted Ceramic Coffee Mug Set (4-Pack)", "qty": 1, "price": "₹2,199.00"},
        ],
        "shipping_address": "Indiranagar, Bengaluru, KA 560038",
    },
    "aanya.k@outlook.com": {
        "order_id": "DS-9780",
        "order_date": "2026-09-16",
        "fulfillment_status": "Delivered",
        "carrier": "Shadowfax",
        "tracking_number": "SF-44910283",
        "tracking_url": "https://shadowfax.in/track",
        "order_total": "₹1,299.00",
        "items": [
            {"title": "Organic Lavender Essential Oil (30ml)", "qty": 1, "price": "₹1,299.00"},
        ],
        "shipping_address": "Vasant Kunj, New Delhi, DL 110070",
    },
    "vikram.m@techcorp.in": {
        "order_id": "DS-9650",
        "order_date": "2026-09-18",
        "fulfillment_status": "Payment Pending Verification",
        "carrier": "Unassigned",
        "tracking_number": "N/A",
        "tracking_url": "#",
        "order_total": "₹2,499.00",
        "items": [
            {"title": "Ergonomic Desk Mat + Wrist Rest Duo", "qty": 1, "price": "₹2,499.00"},
        ],
        "shipping_address": "Cyber City, Gurugram, HR 122002",
    },
    "ananya.j@gmail.com": {
        "order_id": "DS-10022",
        "order_date": "2026-09-20",
        "fulfillment_status": "Processing / Pre-Dispatch",
        "carrier": "Shiprocket Priority",
        "tracking_number": "SR-PENDING",
        "tracking_url": "#",
        "order_total": "₹3,400.00",
        "items": [
            {"title": "Glow Facial Serum 50ml", "qty": 2, "price": "₹2,400.00"},
            {"title": "Hydrating Rose Mist", "qty": 1, "price": "₹1,000.00"},
        ],
        "shipping_address": "Flat 402, Green Glen, Mumbai, MH 400076",
    },
}


class OrderService:
    """Provides simulated Shopify / D2C e-commerce context for support agents."""

    @classmethod
    def get_order_context(
        cls, customer_email: str, text_content: str = ""
    ) -> Optional[Dict[str, Any]]:
        email = customer_email.strip().lower()
        if email in MOCK_ORDERS:
            return MOCK_ORDERS[email]

        # Check for order pattern in text (e.g. #DS-9901 or DS-1234)
        match = re.search(r"(?:order\s*#?|#)([a-zA-Z0-9_-]+)", text_content, re.I)
        if match:
            found_id = match.group(1).upper()
            for _, order in MOCK_ORDERS.items():
                if order["order_id"] == found_id:
                    return order

            # Dynamically construct synthetic order if valid pattern
            return {
                "order_id": f"DS-{found_id[-4:] if len(found_id) >= 4 else '8810'}",
                "order_date": "Recent Order",
                "fulfillment_status": "In Transit",
                "carrier": "BlueDart Express",
                "tracking_number": f"BD-{abs(hash(email)) % 100000000}",
                "tracking_url": "https://track.bluedart.com",
                "order_total": "₹1,999.00",
                "items": [{"title": "D2C Essential Bundle", "qty": 1, "price": "₹1,999.00"}],
                "shipping_address": "Verified Customer Address",
            }

        # Fallback simulated order for any email
        return {
            "order_id": f"DS-{abs(hash(email)) % 9000 + 1000}",
            "order_date": "Recent",
            "fulfillment_status": "Fulfilled",
            "carrier": "Delhivery Express",
            "tracking_number": f"DLV-{abs(hash(email)) % 80000000}",
            "tracking_url": "https://delhivery.com",
            "order_total": "₹1,690.00",
            "items": [{"title": "Standard Store Purchase", "qty": 1, "price": "₹1,690.00"}],
            "shipping_address": "Registered Account Address",
        }
