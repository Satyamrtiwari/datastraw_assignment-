import logging
from typing import List, Optional, Dict, Any

from backend.ai_engine.client import get_groq_client, DEFAULT_MODEL
from backend.ai_engine.prompts import DRAFT_SYSTEM_PROMPT

logger = logging.getLogger(__name__)


class DraftCopilot:
    """
    Real-time Resolution Copilot powered by Groq LLM (Llama 3.3 70B Versatile).
    Drafts empathetic, contextual customer replies incorporating order tracking and internal notes.
    """

    @classmethod
    def generate_draft(
        cls,
        subject: str,
        description: str,
        customer_name: str = "Customer",
        client_name: str = "Aura D2C",
        notes_history: Optional[List[str]] = None,
        order_context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, str]:
        client = get_groq_client()

        if client:
            try:
                context_str = f"Brand: {client_name}\nCustomer Name: {customer_name}\nIssue Subject: {subject}\nDescription: {description}\n"

                if order_context:
                    context_str += (
                        f"\n[Order Context]\n"
                        f"Order ID: {order_context.get('order_id')}\n"
                        f"Status: {order_context.get('fulfillment_status')}\n"
                        f"Carrier: {order_context.get('carrier')}\n"
                        f"Tracking: {order_context.get('tracking_number')}\n"
                    )

                if notes_history:
                    context_str += f"\n[Internal Team Notes]\n" + "\n".join(f"- {n}" for n in notes_history)

                chat_completion = client.chat.completions.create(
                    messages=[
                        {"role": "system", "content": DRAFT_SYSTEM_PROMPT},
                        {"role": "user", "content": f"Please draft the response for the following support ticket:\n{context_str}"},
                    ],
                    model=DEFAULT_MODEL,
                    temperature=0.4,
                    max_tokens=500,
                )

                reply_text = chat_completion.choices[0].message.content.strip()
                return {
                    "suggested_reply": reply_text,
                    "model": f"Groq-{DEFAULT_MODEL}",
                }
            except Exception as e:
                logger.warning(f"Groq draft copilot error, falling back: {e}")

        # Fallback to deterministic AI service
        from backend.app.services.ai_service import AIService
        fallback = AIService.analyze_ticket(
            subject=subject,
            description=description,
            customer_name=customer_name,
            client_name=client_name,
        )
        return {
            "suggested_reply": fallback["suggested_reply"],
            "model": "heuristic-fallback",
        }
