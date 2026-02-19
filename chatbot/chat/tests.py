# FILE: chat/tests.py

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model  # ✅ FIXED - works with custom User model
from unittest.mock import patch
from chat.models import KnowledgeBase, ChatLog
from chat.nlp.chatbot_engine import generate_response, normalize

User = get_user_model()  # ✅ This gets chat.User instead of auth.User


class NormalizeTest(TestCase):
    """Test the normalize() function"""

    def test_lowercase(self):
        self.assertEqual(normalize("HELLO"), "hello")

    def test_strips_whitespace(self):
        self.assertEqual(normalize("  hello  "), "hello")

    def test_removes_special_chars(self):
        self.assertEqual(normalize("what is python???"), "what is python")

    def test_uppercase_with_special(self):
        self.assertEqual(normalize("WHAT IS PYTHON???"), "what is python")


class IntentTest(TestCase):
    """Test intent detection responses"""

    def test_greeting(self):
        response = generate_response("hello")
        self.assertIn("Hello", response)

    def test_farewell(self):
        response = generate_response("bye")
        self.assertIn("Goodbye", response)

    def test_thanks(self):
        response = generate_response("thank you")
        self.assertIn("welcome", response)

    def test_identity(self):
        response = generate_response("who are you")
        self.assertIn("AI", response)

    def test_help(self):
        response = generate_response("help")
        self.assertIn("help", response.lower())

    def test_empty_message(self):
        response = generate_response("")
        self.assertIn("Please type", response)

    def test_whitespace_message(self):
        response = generate_response("   ")
        self.assertIn("Please type", response)


class KnowledgeBaseTest(TestCase):
    """Test Knowledge Base exact match logic"""

    def setUp(self):
        KnowledgeBase.objects.create(
            question="what is python",
            question_display="what is python?",
            answer="Python is a high-level programming language.",
            is_verified=True
        )

    def test_exact_match_returns_cached_answer(self):
        response = generate_response("what is python?")
        self.assertEqual(response, "Python is a high-level programming language.")

    def test_exact_match_uppercase(self):
        response = generate_response("WHAT IS PYTHON?")
        self.assertEqual(response, "Python is a high-level programming language.")

    def test_exact_match_extra_spaces(self):
        response = generate_response("  what is python?  ")
        self.assertEqual(response, "Python is a high-level programming language.")

    def test_no_match_goes_to_gemini(self):
        with patch("chat.nlp.chatbot_engine.generate_detailed_response_gemini") as mock_gemini:
            mock_gemini.return_value = "Django is a web framework."
            response = generate_response("what is django?")
            mock_gemini.assert_called_once()
            self.assertEqual(response, "Django is a web framework.")

    def test_gemini_answer_saved_to_kb(self):
        with patch("chat.nlp.chatbot_engine.generate_detailed_response_gemini") as mock_gemini:
            mock_gemini.return_value = "Django is a web framework."
            generate_response("what is django?")
            saved = KnowledgeBase.objects.filter(question="what is django").first()
            self.assertIsNotNone(saved)
            self.assertEqual(saved.answer, "Django is a web framework.")
            self.assertFalse(saved.is_verified)

    def test_second_ask_uses_kb_not_gemini(self):
        with patch("chat.nlp.chatbot_engine.generate_detailed_response_gemini") as mock_gemini:
            mock_gemini.return_value = "Django is a web framework."
            generate_response("what is django?")
            self.assertEqual(mock_gemini.call_count, 1)
            generate_response("what is django?")
            self.assertEqual(mock_gemini.call_count, 1)  # Still 1, not 2


class GeminiFailureTest(TestCase):
    """Test behavior when Gemini fails"""

    def test_gemini_failure_returns_fallback(self):
        with patch("chat.nlp.chatbot_engine.generate_detailed_response_gemini") as mock_gemini:
            mock_gemini.return_value = None
            response = generate_response("what is rust?")
            self.assertIn("still learning", response)

    def test_gemini_failure_saves_empty_question(self):
        with patch("chat.nlp.chatbot_engine.generate_detailed_response_gemini") as mock_gemini:
            mock_gemini.return_value = None
            generate_response("what is rust?")
            saved = KnowledgeBase.objects.filter(question="what is rust").first()
            self.assertIsNotNone(saved)
            self.assertEqual(saved.answer, "")


class AjaxChatViewTest(TestCase):
    """Test the AJAX chat endpoint"""

    def setUp(self):
        self.client = Client()
        # ✅ Uses get_user_model() so works with custom chat.User
        self.user = User.objects.create_user(
            username="testuser",
            password="testpass123"
        )
        self.client.login(username="testuser", password="testpass123")

    def test_post_returns_200(self):
        with patch("chat.nlp.chatbot_engine.generate_detailed_response_gemini") as mock_gemini:
            mock_gemini.return_value = "Test answer"
            response = self.client.post(
                reverse("ajax_chat"),
                {"message": "what is python?"},
            )
            self.assertEqual(response.status_code, 200)

    def test_post_returns_json(self):
        with patch("chat.nlp.chatbot_engine.generate_detailed_response_gemini") as mock_gemini:
            mock_gemini.return_value = "Test answer"
            response = self.client.post(
                reverse("ajax_chat"),
                {"message": "what is python?"},
            )
            self.assertIn("application/json", response["Content-Type"])

    def test_post_returns_correct_response(self):
        with patch("chat.nlp.chatbot_engine.generate_detailed_response_gemini") as mock_gemini:
            mock_gemini.return_value = "Test answer"
            response = self.client.post(
                reverse("ajax_chat"),
                {"message": "what is python?"},
            )
            data = response.json()
            self.assertIn("bot_response", data)

    def test_empty_message_returns_400(self):
        response = self.client.post(
            reverse("ajax_chat"),
            {"message": ""},
        )
        self.assertEqual(response.status_code, 400)

    def test_get_not_allowed(self):
        response = self.client.get(reverse("ajax_chat"))
        self.assertEqual(response.status_code, 405)

    def test_chat_log_saved(self):
        with patch("chat.nlp.chatbot_engine.generate_detailed_response_gemini") as mock_gemini:
            mock_gemini.return_value = "Test answer"
            self.client.post(
                reverse("ajax_chat"),
                {"message": "what is python?"},
            )
            log = ChatLog.objects.filter(user=self.user).first()
            self.assertIsNotNone(log)
            self.assertEqual(log.user_message, "what is python?")

    def test_unauthenticated_redirects(self):
        self.client.logout()
        response = self.client.post(
            reverse("ajax_chat"),
            {"message": "what is python?"},
        )
        self.assertEqual(response.status_code, 302)