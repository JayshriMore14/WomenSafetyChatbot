"""Emergency alert and SOS helpers."""

from __future__ import annotations

import os
from datetime import datetime

try:
    from twilio.rest import Client
except Exception:  # pragma: no cover - optional runtime dependency
    Client = None


EMERGENCY_INSTRUCTIONS = [
    "Move toward a public, well-lit, or staffed area.",
    "Call your local emergency number immediately if there is direct danger.",
    "Share your live location with trusted contacts.",
    "Speak loudly and clearly: I need help.",
    "Avoid confrontation when escape is possible.",
]


def build_emergency_message(location_message: str | None = None) -> str:
    """Create the emergency alert message."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    location_text = location_message or "Location not available."
    return f"Emergency SOS triggered at {timestamp}. {location_text} Please check immediately."


def simulate_emergency_notification(contacts: list[dict], location_message: str | None = None) -> list[str]:
    """Return simulated notification messages for display."""
    message = build_emergency_message(location_message)
    if not contacts:
        return [f"Simulated alert prepared: {message}"]
    return [f"Simulated alert sent to {contact['name']} ({contact['phone']}): {message}" for contact in contacts]


def send_twilio_sms_if_configured(to_number: str, message: str) -> str:
    """Send SMS only when Twilio environment variables are configured.

    This keeps the app beginner-safe. Without credentials, it returns a simulated
    status and never fails the emergency flow.
    """
    required = {
        "TWILIO_ACCOUNT_SID": os.getenv("TWILIO_ACCOUNT_SID"),
        "TWILIO_AUTH_TOKEN": os.getenv("TWILIO_AUTH_TOKEN"),
        "TWILIO_FROM_NUMBER": os.getenv("TWILIO_FROM_NUMBER"),
    }

    if not all(required.values()) or Client is None:
        return f"Simulation mode: SMS would be sent to {to_number}."

    client = Client(required["TWILIO_ACCOUNT_SID"], required["TWILIO_AUTH_TOKEN"])
    sms = client.messages.create(
        body=message,
        from_=required["TWILIO_FROM_NUMBER"],
        to=to_number,
    )
    return f"Twilio SMS sent to {to_number}. SID: {sms.sid}"
