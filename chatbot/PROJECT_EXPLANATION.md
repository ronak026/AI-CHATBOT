# AI Chatbot — Project Explanation

This document explains how the AI Chatbot project is built, how data flows, and how each part works together.

---

## 1. What the Project Does

The **AI Chatbot** is a web application where:

- Users **register** and **log in**.
- Logged-in users **chat** with an AI that answers questions and can generate code.
- The bot **learns**: new answers from the Google Gemini API are stored in a **knowledge base** and reused for similar questions later.
- Users can view **chat history** and update their **profile** (including avatar).

The stack is **Django** (backend), **Tailwind CSS** (styling), and **Google Gemini API** (AI responses).

---

## 2. High-Level Architecture

```
┌─────────────────┐     HTTP/HTTPS      ┌──────────────────┐
│   Browser       │ ◄────────────────► │   Django Server  │
│   (HTML/JS)     │                    │   (views, URLs)  │
└─────────────────┘                    └────────┬─────────┘
                                                │
                    ┌───────────────────────────┼───────────────────────────┐
                    │                           │                           │
                    ▼                           ▼                           ▼
            ┌───────────────┐           ┌───────────────┐           ┌───────────────┐
            │   Models      │           │   NLP Engine  │           │   Gemini API  │
            │   (DB)        │           │   (intent,    │           │   (external)  │
            │ User, ChatLog,│           │  vectorizer, │           │               │
            │ KnowledgeBase │           │  chatbot)     │           └───────────────┘
            └───────────────┘           └───────────────┘
```

- **Browser**: Renders HTML templates, sends form and AJAX requests.
- **Django**: Handles URLs, views, auth, forms, and calls the NLP engine and DB.
- **Models**: Store users, chat logs, and knowledge base entries.
- **NLP Engine**: Normalizes text, detects intent, matches questions to the knowledge base, and calls Gemini when needed.
- **Gemini API**: Provides answers for questions not in the knowledge base.

---

## 3. Backend Components

### 3.1 Django Project Structure

- **`chatbot/`** (project package): `settings.py`, root `urls.py`, `wsgi.py`.
- **`chat/`** (app): All chat-related code — models, views, forms, URLs, and the `nlp/` package.
- **`theme/`**: Tailwind CSS theme (django-tailwind).

### 3.2 Models (`chat/models.py`)

| Model           | Purpose |
|----------------|--------|
| **User**       | Custom user (extends Django’s `AbstractUser`). Adds `avatar` (image). Used for login and profile. |
| **ChatLog**    | One row per user message + bot response. Fields: `user`, `user_message`, `bot_response`, `created_at`. |
| **KnowledgeBase** | Cached Q&A. `question` (normalized, unique), `question_display` (original), `answer`, `is_verified`, `created_at`. |

- User and ChatLog are for **per-user** data.
- KnowledgeBase is **global**: any user can get an answer from the same cached question.

### 3.3 Views (`chat/views.py`)

| View              | URL (name)   | What it does |
|-------------------|-------------|--------------|
| `home_view`       | `/` (home)  | Renders landing page. |
| `register_view`   | `/register/`| GET: show form. POST: create user, log in, redirect home. |
| `login_view`      | `/login/`   | GET: show form. POST: authenticate, login or show error. |
| `logout_view`     | `/logout/`  | Logs out, redirects to login. |
| `chat_view`       | `/chat/`    | Login required. GET: show chat page. POST: handle non-AJAX message (optional). |
| `ajax_chat_view`  | `/ajax/chat/` | Login required. POST only. Receives `message`, returns JSON `{ user_message, bot_response }`. Used by the chat UI. |
| `chat_history_view`| `/history/` | Login required. Lists current user’s ChatLogs. |
| `profile_view`    | `/profile/` | Login required. GET: show form. POST: update user (username, email, avatar). |

Chat is **driven by AJAX**: the page loads once, and each “Send” uses `ajax_chat_view` so the page doesn’t reload.

### 3.4 Response Generation Flow (`chat/nlp/chatbot_engine.py`)

When the user sends a message, `generate_response(user_message)` runs:

1. **Empty check**  
   If the message is empty or only whitespace → return a short “Please type a message” style response.

2. **Normalize**  
   `normalize(text)`: lowercase, strip, remove non-word characters. Used for matching and storage.

3. **Intent detection** (`chat/nlp/intent.py`)  
   If the normalized text matches known intents (greeting, farewell, thanks, identity, help), return a fixed reply and **stop**. No DB or API call.

4. **Exact match in KnowledgeBase**  
   Look up `KnowledgeBase` by normalized `question`. If found → return that row’s `answer` and stop.

5. **Similarity match (TF-IDF)**  
   If there are knowledge base entries, use `ChatbotVectorizer` (TF-IDF + cosine similarity) to find the best matching question. If best score ≥ 0.6 → return that entry’s answer and stop.

6. **Gemini fallback**  
   Call `generate_detailed_response_gemini(user_message)` (Google Gemini). If it returns text:
   - Store in KnowledgeBase: `question` = normalized, `question_display` = original, `answer` = Gemini response, `is_verified` = False.
   - Return that response.

7. **Final fallback**  
   If Gemini fails or returns nothing: optionally store the normalized question for “learning” and return a message like “I’ve saved this for future training.”

So: **intent → exact KB → similar KB → Gemini → save and reply or fallback.**

### 3.5 Supporting NLP Modules

- **`intent.py`**: Keyword/pattern list per intent; `detect_intent(text)` returns intent name or `"unknown"`.
- **`vectorizer.py`**: `ChatbotVectorizer(questions)`. `find_best_match(user_input)` returns `(index, confidence)` using TF-IDF and cosine similarity.
- **`preprocess.py`**: `clean_text(text)` — lowercase, remove special chars, tokenize, remove stopwords (for any preprocessing that needs it).
- **`code_formatter.py`**: Format code for display; detect if a response is “code” (e.g. for front-end rendering).
- **`gemini_code_gen.py`**: Detect “code request” vs “explain something”, extract language, call Gemini for code if needed (used as part of or alongside the main engine flow).

### 3.6 Forms (`chat/forms.py`)

- **RegisterForm**: UserCreationForm + email + avatar. Creates `User`, sets email, optional avatar.
- **ProfileUpdateForm**: ModelForm for User with fields username, email, avatar. Used on profile page.

### 3.7 Configuration

- **`chatbot/settings.py`**: `AUTH_USER_MODEL = 'chat.User'`, `LOGIN_URL` / `LOGIN_REDIRECT_URL` / `LOGOUT_REDIRECT_URL`, static/media, Crispy Forms (Tailwind), REST framework, `GEMINI_API_KEY` from environment (e.g. `.env` via python-dotenv).
- **Environment**: `GEMINI_API_KEY` is required for Gemini; without it, only intent and knowledge-base answers work.

---

## 4. Frontend (HTML Pages) Explanation

All main pages extend **`base.html`**, which provides:

- Common layout: navbar (logo, Home, Chat, Profile, History, Login/Logout), main content block, footer.
- Tailwind CSS (via `{% tailwind_css %}`).
- Lucide icons (`data-lucide`), and small CSS for icon hover and pulse.
- `{% block title %}` and `{% block content %}` for page-specific content.

### 4.1 `base.html`

- **Navbar**: Links to home, chat, profile, history. If authenticated: Logout. Else: Login.
- **Main**: `{% block content %}` — each page fills this.
- **Footer**: Short line (e.g. “AI Chatbot • Built with Django & Tailwind”).

So every page shares the same header and footer; only the middle part changes.

### 4.2 `home.html`

- **Hero**: Title, short description, “Start Chatting” button (links to chat).
- **Features**: Three cards (e.g. Intelligent Answers, Self-Learning, Fast Responses).
- **How it works**: Three steps (Ask → AI understands → Smart reply).
- **CTA**: “Chat Now” button.
- **JS**: Simple typing effect on one line of the hero (e.g. “learns.” / “responds.” / “remembers.”).

Purpose: landing/marketing page before login.

### 4.3 `auth/login.html`

- Back link.
- Centered card: logo, “Welcome Back”, login form (username, password, CSRF), submit button, link to register.
- Django `messages` for errors (e.g. “Invalid username or password”).

### 4.4 `auth/register.html`

- Back link.
- Centered card: register form (username, email, avatar, password1, password2), CSRF, submit, link to login.
- Uses Crispy/Tailwind for form styling.

### 4.5 `chat/chat.html`

- **Header**: “AI Chatbot”, “Online & Learning” badge.
- **Chat area**: Scrollable div with a welcome message from the bot. User and bot messages are appended here by JavaScript.
- **Input**: Text field + “Send” button.
- **Behavior**:
  - On submit (JS): prevent default, read message, append user bubble, show “Thinking…”, POST to `{% url 'ajax_chat' %}` with CSRF and `message`.
  - On success: remove “Thinking…”, append bot reply. Bot reply is formatted by JS: code blocks (e.g. `# PYTHON CODE` + numbered lines) get a code-style box and “Copy Code”; other text is formatted (headers, lists, bold, inline code).
  - No full page reload; all chat is via AJAX.

So the “HTML page” for chat is one screen; the conversation is built dynamically with JS and the AJAX endpoint.

### 4.6 `chat/history.html`

- Lists the current user’s chat logs (e.g. user message, bot response, date). Usually a table or list of cards. No JavaScript needed for basic listing.

### 4.7 `profile.html`

- Form to update username, email, avatar. POST to same profile view. Success message after save.

---

## 5. Data Flow Examples

### 5.1 User Sends a Chat Message

1. User types in chat and clicks Send.
2. JS sends POST to `/ajax/chat/` with `message` and CSRF.
3. `ajax_chat_view` runs: checks login, gets `message`, calls `generate_response(message)`.
4. Inside `generate_response`: intent → exact KB → similarity KB → Gemini (and optional save) → return text.
5. View creates a `ChatLog` (user, user_message, bot_response), returns JSON `{ user_message, bot_response }`.
6. JS receives JSON, formats `bot_response` (code vs text), appends user and bot bubbles to the chat area.

### 5.2 First Time vs Second Time Asking the Same Question

- **First time**: No intent match, no exact/similar KB match → Gemini is called → response is stored in KnowledgeBase (normalized question + display + answer) → same response returned.
- **Second time** (same or very similar question): Exact or high-similarity match in KnowledgeBase → stored answer returned without calling Gemini.

### 5.3 Login and Permissions

- Login and register use Django’s `authenticate`, `login`, and session.
- `@login_required` on chat, history, profile, and ajax_chat. Unauthenticated requests redirect to login.
- Chat history and profile are filtered by `request.user`, so each user sees only their own data.

---

## 6. Summary Table

| Layer        | Main components |
|-------------|------------------|
| **URLs**    | `/`, `/login/`, `/register/`, `/logout/`, `/chat/`, `/ajax/chat/`, `/history/`, `/profile/`. |
| **Views**   | Home, auth (register, login, logout), chat (page + AJAX), history, profile. |
| **Models**  | User (with avatar), ChatLog, KnowledgeBase. |
| **NLP**     | Intent, normalize, exact/similar KB match, Gemini, code formatter/detection. |
| **Templates** | base → home, login, register, chat, history, profile. |
| **Frontend** | Tailwind, Lucide, vanilla JS for chat AJAX and formatting. |

This is the full explanation of how the project and its HTML pages work end to end.
