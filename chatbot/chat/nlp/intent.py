# FILE 3: chat/nlp/intent.py
# This file detects user intents (greeting, farewell, help, etc.)

import re
from typing import Dict, List


INTENTS: Dict[str, List[str]] = {
    "greeting": [
        "hello", "hi", "hey", "good morning", "good evening", 
        "good afternoon", "morning", "evening", "afternoon",
        "hy", "hy there", "wassup", "howdy"
    ],
    "farewell": [
        "bye", "goodbye", "see you", "take care", "later", "by",
        "exit", "quit", "leave"
    ],
    "thanks": [
        "thanks", "thank you", "thx", "thank u", "appreciate it",
        "thankyou", "thnx"
    ],
    "identity": [
        "who are you", "what are you", "who r u", "what r u", 
        "tell me about yourself", "introduce yourself", "about you"
    ],
    "help": [
        "help", "can you help", "i need help", "please help", 
        "assist me", "help me", "help please", "need assistance"
    ],
}


def detect_intent(text: str) -> str:
    """
    Detect user intent safely using word boundaries.
    Returns the intent type or "unknown" if no match found.
    """

    if not isinstance(text, str) or not text.strip():
        return "unknown"

    normalized_text = text.lower().strip()

    for intent, keywords in INTENTS.items():
        for keyword in keywords:
            # Match whole words only (prevents false positives)
            pattern = rf"\b{re.escape(keyword)}\b"
            if re.search(pattern, normalized_text):
                return intent

    return "unknown"