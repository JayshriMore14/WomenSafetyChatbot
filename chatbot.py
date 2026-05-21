"""Offline chatbot logic for women safety guidance.

The chatbot uses predefined responses, spaCy tokenization, and keyword matching.
It does not call any external AI API.
"""

from __future__ import annotations

import re

import spacy


try:
    NLP = spacy.load("en_core_web_sm")
except OSError:
    NLP = spacy.blank("en")


DANGER_KEYWORDS = {
    "help",
    "danger",
    "unsafe",
    "stalker",
    "emergency",
    "trapped",
    "followed",
    "threat",
    "attack",
    "scared",
}


SAFETY_RESPONSES = {
    "night_travel": {
        "keywords": {"night", "late", "travel", "cab", "taxi", "walking"},
        "response": (
            "For night travel, share your live location with a trusted contact, use well-lit roads, "
            "avoid isolated shortcuts, verify cab details, sit near the driver-side rear door, and keep "
            "emergency contacts ready."
        ),
    },
    "cyber_safety": {
        "keywords": {"cyber", "password", "privacy", "account", "otp", "online", "social"},
        "response": (
            "For cyber safety, use strong passwords, enable two-factor authentication, avoid sharing OTPs, "
            "block suspicious users, preserve screenshots, and report impersonation or threats immediately."
        ),
    },
    "public_transport": {
        "keywords": {"bus", "train", "metro", "transport", "station", "public"},
        "response": (
            "In public transport, stay near families or women passengers, avoid empty compartments, keep "
            "your bag close, note emergency exits, and alert staff or police if someone makes you uncomfortable."
        ),
    },
    "self_defense": {
        "keywords": {"defense", "defence", "attack", "escape", "protect", "pepper"},
        "response": (
            "Focus on escape, not fighting. Create distance, shout clearly, target vulnerable areas only if "
            "needed, move toward people or light, and call emergency services as soon as possible."
        ),
    },
    "online_harassment": {
        "keywords": {"harassment", "abuse", "blackmail", "message", "threat", "stalking"},
        "response": (
            "For online harassment, do not engage with the abuser. Save screenshots, profile links, phone "
            "numbers, and timestamps. Block the person and report through platform tools and local cyber cells."
        ),
    },
    "mental_support": {
        "keywords": {"anxious", "panic", "afraid", "crying", "alone", "stress", "worried", "scared"},
        "response": (
            "Take one slow breath in and one slow breath out. You are taking action now. Move to a safer, "
            "visible place if possible, contact someone trusted, and use SOS if there is immediate danger."
        ),
    },
}


DEFAULT_RESPONSE = (
    "I can help with night travel safety, cyber safety, public transport safety, self-defense guidance, "
    "online harassment help, emergency support, and nearby help centers."
)


def normalize_message(message: str) -> str:
    """Normalize user text for matching."""
    return re.sub(r"\s+", " ", message or "").strip().lower()


def detect_danger_keywords(message: str) -> list[str]:
    """Return danger keywords found in the message."""
    normalized = normalize_message(message)
    tokens = {token.text.lower() for token in NLP(normalized)}
    found = sorted(tokens.intersection(DANGER_KEYWORDS))

    for keyword in DANGER_KEYWORDS:
        if re.search(rf"\b{re.escape(keyword)}\b", normalized) and keyword not in found:
            found.append(keyword)

    return found


def get_chatbot_response(message: str) -> tuple[str, bool, list[str]]:
    """Return response text, emergency flag, and detected danger words."""
    danger_words = detect_danger_keywords(message)
    normalized = normalize_message(message)
    tokens = {token.text.lower() for token in NLP(normalized)}

    for response_data in SAFETY_RESPONSES.values():
        if tokens.intersection(response_data["keywords"]):
            return response_data["response"], bool(danger_words), danger_words

    if danger_words:
        return (
            "Emergency words detected. Move to a visible public place if possible, press SOS, share your "
            "location, and call your local emergency number immediately.",
            True,
            danger_words,
        )

    return DEFAULT_RESPONSE, False, danger_words
