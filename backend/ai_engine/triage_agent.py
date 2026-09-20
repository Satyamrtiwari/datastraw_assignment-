import json
import logging
from typing import Dict, Any

from backend.ai_engine.client import get_groq_client, DEFAULT_MODEL
from backend.ai_engine.prompts import TRIAGE_SYSTEM_PROMPT

logger = logging.getLogger(__name__)


class TriageAgent:
    """
    Autonomous Support Triage Agent powered by Groq LLM (Llama 3.3 70B Versatile).
    Extracts urgency, category, 1-sentence executive summary, and 1-click suggested reply.
    """

    @classmethod
    def analyze_ticket(
        cls,
        subject: str,
        description: str,
        customer_name: str = "Customer",
        client_name: str = "Aura D2C",
    ) -> Dict[str, Any]:
        client = get_groq_client()

        if client:
            try:
                user_content = (
                    f"Brand: {client_name}\n"
                    f"Customer Name: {customer_name}\n"
                    f"Ticket Subject: {subject}\n"
                    f"Ticket Description: {description}"
                )

                chat_completion = client.chat.completions.create(
                    messages=[
                        {"role": "system", "content": TRIAGE_SYSTEM_PROMPT},
                        {"role": "user", "content": user_content},
                    ],
                    model=DEFAULT_MODEL,
                    temperature=0.2,
                    response_format={"type": "json_object"},
                    max_tokens=600,
                )

                content = chat_completion.choices[0].message.content
                parsed = json.loads(content)

                # Validate expected keys with fallbacks
                priority = parsed.get("priority", "Normal")
                if priority not in ["Urgent", "High", "Medium", "Normal"]:
                    priority = "Normal"

                category = parsed.get("category", "General Inquiry")
                summary = parsed.get("ai_summary") or f"Customer inquiry: {subject[:60]}"
                suggested_reply = parsed.get("suggested_reply") or f"Hi {customer_name},\n\nThank you for reaching out..."

                return {
                    "priority": priority,
                    "category": category,
                    "ai_summary": summary,
                    "suggested_reply": suggested_reply,
                    "confidence_score": 0.98,
                    "model": f"Groq-{DEFAULT_MODEL}",
                }
            except Exception as e:
                logger.warning(f"Groq API call failed or timed out, using intelligent fallback: {e}")

        # Graceful fallback to deterministic heuristic engine
        from backend.app.services.ai_service import AIService
        return AIService.analyze_ticket(
            subject=subject,
            description=description,
            customer_name=customer_name,
            client_name=client_name,
        )
