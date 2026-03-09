"""
Message Agent — Generates personalized, multilingual reminder messages.
Uses language templates first, then optionally polishes with GPT-4o Mini.
"""

import logging
from datetime import date

from app.languages.detector import get_language
from app.models.appointment import Appointment
from app.models.patient import Patient
from app.models.tenant import Tenant
from app.services.openai_service import openai_service
from app.specialty import get_specialty

logger = logging.getLogger("careremind.agents.message")


class MessageAgent:
    """Generates reminder messages using templates + optional AI polish."""

    async def generate(
        self,
        patient: Patient,
        appointment: Appointment,
        tenant: Tenant,
        use_ai_polish: bool = False,
    ) -> str:
        """
        Generate a personalized reminder message.

        1. Get the language template for the patient's preferred language
        2. Fill in placeholders with real data
        3. Optionally polish with GPT-4o Mini for natural-sounding text
        """
        # Get specialty and language
        specialty_name = appointment.specialty_override or tenant.specialty
        specialty = get_specialty(specialty_name)
        language = get_language(patient.language_preference or tenant.language_preference)

        # Format the date
        visit_date = appointment.next_visit_date or appointment.visit_date
        formatted_date = language.format_date(visit_date) if visit_date else "TBD"

        # Build the message from template
        template = language.get_reminder_template()
        message = template.format(
            patient_name=patient.name,
            doctor_name=tenant.doctor_name,
            clinic_name=tenant.clinic_name or "our clinic",
            date=formatted_date,
            pre_visit_instructions=specialty.get_pre_visit_instructions(),
        )

        # Optionally polish with AI for more natural language
        if use_ai_polish and openai_service.api_key:
            try:
                polished = await openai_service.chat(
                    prompt=(
                        f"Rewrite this clinic reminder message to sound more natural and warm "
                        f"in {language.get_language_name()}. Keep it short (under 160 chars for SMS). "
                        f"Keep all the factual information unchanged. Tone: {specialty.get_tone()}.\n\n"
                        f"Original:\n{message}"
                    ),
                    system="You are a medical clinic assistant writing patient reminders.",
                )
                if polished:
                    message = polished
            except Exception as e:
                logger.warning("AI polish failed, using template: %s", e)

        return message
