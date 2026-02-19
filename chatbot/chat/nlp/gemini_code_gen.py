# FILE 1: chat/nlp/gemini_code_gen.py
# This file handles code generation with Google Gemini

from google import genai  # ✅ FIXED IMPORT
import os
from typing import Optional


def get_api_key():
    """Get API key from environment, with fallback"""
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        print("⚠️  WARNING: GEMINI_API_KEY not found. Code generation will be disabled.")
        print("Please set your API key in your .env file: GEMINI_API_KEY=your-key-here")
        return None

    return api_key


GEMINI_API_KEY = get_api_key()
# ✅ REMOVED: genai.configure() - not needed with new SDK


def detect_code_request(text: str) -> bool:
    """
    Check if user is explicitly asking for code generation.

    Fixed to avoid false positives like:
    - "tell me about java" → NOT a code request
    - "what is python" → NOT a code request
    - "write a python function" → IS a code request
    - "create a loop in javascript" → IS a code request
    """
    text_lower = text.lower()

    # Keywords that indicate explicit code request
    explicit_code_keywords = [
        "write", "create", "generate", "build", "implement", "code",
        "function", "class", "script", "program", "snippet", "example",
        "show me", "can you", "help me", "make", "how to", "write a",
        "create a", "build a", "make a", "implement a"
    ]

    # Keywords that indicate explanation request (NOT code)
    explanation_keywords = [
        "what is", "tell me about", "explain", "describe", "difference between",
        "how does", "what are", "definition", "meaning", "understand",
        "learn about", "know about", "info about", "information about",
        "tutorial on", "guide to", "about"
    ]

    # Check for explanation keywords first - they take precedence
    for keyword in explanation_keywords:
        if keyword in text_lower:
            return False

    # Check for explicit code keywords
    has_code_keyword = any(keyword in text_lower for keyword in explicit_code_keywords)

    # Also check if user is asking for code for a specific task
    if "code" in text_lower or "code for" in text_lower:
        return True

    return has_code_keyword


def generate_code_free(user_message: str, language: str = "python") -> Optional[str]:
    """
    Generate code using Google Gemini API (FREE).

    Args:
        user_message: The user's code request
        language: Programming language (default: python)

    Returns:
        Generated code or None if failed
    """

    if not GEMINI_API_KEY:
        return None

    if not user_message or not user_message.strip():
        return None

    try:
        client = genai.Client(api_key=GEMINI_API_KEY)  # ✅ CORRECT

        system_prompt = f"""You are a helpful programming assistant. 
When asked to write code, provide clean, well-commented code in {language}.
Keep responses concise and practical.
Always include:
- Clear variable names
- Comments explaining complex logic
- Example usage if applicable

If the request is unclear, ask for clarification."""

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=f"{system_prompt}\n\nUser request: {user_message}",
        )

        if response.text:
            return response.text
        else:
            return None

    except Exception as e:
        print(f"❌ Error generating code with Gemini: {e}")
        return None


def extract_language(text: str) -> str:
    """
    Try to detect programming language from user message.
    """
    language_map = {
        "python": ["python", "py"],
        "javascript": ["javascript", "js", "node"],
        "java": ["java"],
        "sql": ["sql", "database", "query"],
        "html": ["html"],
        "css": ["css"],
        "cpp": ["c++", "cpp"],
        "csharp": ["c#", "csharp", "c sharp"],
        "ruby": ["ruby"],
        "php": ["php"],
        "go": ["go", "golang"],
    }

    text_lower = text.lower()

    for lang, keywords in language_map.items():
        for keyword in keywords:
            if keyword in text_lower:
                return lang

    return "python"  # Default to Python