# FILE: chat/nlp/chatbot_engine.py
# Flow: Intent → Exact KB match → Gemini → Save to KB

from .intent import detect_intent
from chat.models import KnowledgeBase
import re
from google import genai
import os

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
DAILY_REQUEST_LIMIT = 20


def normalize(text: str) -> str:
    """Normalize text - lowercase and remove special chars"""
    text = text.strip().lower()
    text = re.sub(r"[^\w\s]", "", text)
    return text


def generate_detailed_response_gemini(user_message: str) -> str:
    """Generate detailed, well-structured response using Gemini."""
    if not GEMINI_API_KEY:
        return None

    if not user_message or not user_message.strip():
        return None

    try:
        client = genai.Client(api_key=GEMINI_API_KEY)

        system_prompt = """You are a helpful AI assistant that provides detailed, well-structured responses.

When providing answers:
1. Start with a clear explanation or introduction
2. Include practical examples or code snippets
3. Use clear section headers for different parts
4. If code is involved, provide multiple approaches or explain the concept thoroughly
5. Format responses with good readability
6. Do NOT include the question as the first line - go straight to the answer

For code requests:
- Provide complete, working code
- Add comments explaining the logic
- Include usage examples
- Explain the approach

For explanations:
- Start with a simple definition
- Provide detailed explanation
- Include practical examples
- Add key points or benefits

Make responses informative, well-organized, and easy to understand."""

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=f"{system_prompt}\n\nUser question/request: {user_message}",
        )

        return response.text if response.text else None

    except Exception as e:
        print(f"❌ Error generating response with Gemini: {e}")
        return None


def check_user_limit(user) -> bool:
    if user is None:
        return True
    from chat.models import UserRequestLimit
    limit, _ = UserRequestLimit.objects.get_or_create(user=user)
    limit.reset_if_new_day()
    return limit.can_make_request()


def increment_user_limit(user) -> None:
    if user is None:
        return
    from chat.models import UserRequestLimit
    limit, _ = UserRequestLimit.objects.get_or_create(user=user)
    limit.increment()


def get_remaining_requests(user) -> int:
    if user is None:
        return DAILY_REQUEST_LIMIT
    from chat.models import UserRequestLimit
    limit, _ = UserRequestLimit.objects.get_or_create(user=user)
    limit.reset_if_new_day()
    return max(0, DAILY_REQUEST_LIMIT - limit.request_count)


def generate_response(user_message: str, user=None) -> str:
    """
    Main flow:
    1. Intent handling         → FREE
    2. Exact match in KB       → FREE
    3. Check user daily limit
    4. Ask Gemini              → COSTS 1 request
    5. Save to KB
    """

    if not user_message or not user_message.strip():
        return "Please type a message 😊"

    user_message_norm = normalize(user_message)

    # ============ STEP 1: INTENT HANDLING ============
    intent = detect_intent(user_message_norm)

    if intent == "greeting":
        return "Hello 😊 How can I help you today?"
    if intent == "farewell":
        return "Goodbye 👋 Have a great day!"
    if intent == "thanks":
        return "You're welcome! 😊"
    if intent == "identity":
        return "I'm an AI chatbot that learns from conversations! I save questions I don't know and improve over time. Feel free to teach me anything! 🤖"
    if intent == "help":
        return (
            "I'm here to help! You can ask me questions on various topics, "
            "and I can even write code for you FREE! 💻 Feel free to teach me anything! 😊"
        )

    # ============ STEP 2: EXACT MATCH IN KB ============
    exact = KnowledgeBase.objects.filter(question=user_message_norm).first()
    if exact:
        print(f"✅ Exact match: '{user_message_norm[:50]}'")
        return exact.answer

    # ============ STEP 3: CHECK USER DAILY LIMIT ============
    if not check_user_limit(user):
        print(f"🚫 User {user} has reached daily limit")
        return (
            "⚠️ You've reached your **20 daily request limit** for new questions.\n\n"
            "Your limit resets tomorrow. In the meantime:\n"
            "- Try rephrasing questions you've already asked\n"
            "- Questions already in our knowledge base are **unlimited** and free! 😊"
        )

    # ============ STEP 4: ASK GEMINI ============
    print(f"⏳ Asking Gemini: '{user_message[:50]}'...")
    detailed_response = generate_detailed_response_gemini(user_message)

    if detailed_response:
        # ============ STEP 5: INCREMENT + SAVE TO KB ============
        increment_user_limit(user)
        remaining = get_remaining_requests(user)
        print(f"📊 User {user} — {remaining} requests remaining today")

        KnowledgeBase.objects.update_or_create(
            question=user_message_norm,
            defaults={
                "question_display": user_message,
                "answer": detailed_response,
                "is_verified": False
            }
        )
        print(f"💾 Saved to KB")
        return detailed_response

    # ============ STEP 6: FINAL FALLBACK ============
    _auto_learn(user_message_norm)
    return "I'm still learning 🤖. I've saved this question for future training."


def _auto_learn(user_message_norm: str) -> None:
    """Save question to KB for manual training later"""
    KnowledgeBase.objects.get_or_create(
        question=user_message_norm,
        defaults={
            "question_display": user_message_norm,
            "answer": "",
            "is_verified": False
        }
    )