# AI Chatbot Application

A powerful Django-based AI chatbot application powered by Google Gemini API. This application provides an intelligent conversational interface with features like user authentication, chat history, knowledge base management, and code generation capabilities.

## 🚀 Features

- **AI-Powered Conversations**: Interactive chatbot powered by Google Gemini 2.5 Flash
- **User Authentication**: Secure user registration, login, and profile management
- **Chat History**: Track and view all your previous conversations
- **Knowledge Base**: Intelligent knowledge base system with similarity matching using TF-IDF vectorization
- **Code Generation**: Generate code snippets in multiple programming languages
- **Intent Recognition**: Smart intent detection for greetings, farewells, and more
- **Modern UI**: Beautiful, responsive interface built with Tailwind CSS and DaisyUI
- **User Profiles**: Customizable user profiles with avatar support

## 📋 Prerequisites

Before you begin, ensure you have the following installed:

- Python 3.8 or higher
- Node.js and npm (for Tailwind CSS)
- Google Gemini API key ([Get one here](https://makersuite.google.com/app/apikey))

## 🛠️ Installation

### 1. Clone the Repository

```bash
git clone <repository-url>
cd Ai-chatbot/Chat/chatbot
```

### 2. Create Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 4. Install NLTK Data

```python
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')"
```

### 5. Download spaCy Language Model

```bash
python -m spacy download en_core_web_sm
```

### 6. Install Node Dependencies

```bash
npm install
```

### 7. Environment Configuration

Create a `.env` file in the `chatbot` directory:

```env
GEMINI_API_KEY=your_gemini_api_key_here
SECRET_KEY=your_django_secret_key_here
DEBUG=True
```

### 8. Database Setup

```bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
```

### 9. Collect Static Files

```bash
python manage.py collectstatic
```

### 10. Run Development Server

```bash
python manage.py runserver
```

The application will be available at `http://127.0.0.1:8000/`

## 📁 Project Structure

```
chatbot/
├── chat/                    # Main chat application
│   ├── nlp/                 # NLP processing modules
│   │   ├── chatbot_engine.py    # Main chatbot logic
│   │   ├── gemini_code_gen.py   # Code generation
│   │   ├── intent.py            # Intent detection
│   │   ├── vectorizer.py        # TF-IDF vectorization
│   │   ├── preprocess.py        # Text preprocessing
│   │   └── code_formatter.py    # Code formatting
│   ├── models.py            # Database models
│   ├── views.py             # View functions
│   ├── forms.py             # Django forms
│   └── urls.py              # URL routing
├── chatbot/                 # Django project settings
│   ├── settings.py          # Project configuration
│   ├── urls.py              # Root URL configuration
│   └── wsgi.py              # WSGI configuration
├── templates/               # HTML templates
│   ├── auth/                # Authentication templates
│   ├── chat/                # Chat interface templates
│   └── base.html            # Base template
├── theme/                   # Tailwind CSS theme
├── media/                   # User uploaded files
├── static/                  # Static files
├── requirements.txt         # Python dependencies
├── package.json            # Node.js dependencies
└── manage.py               # Django management script
```

## 🔧 Configuration

### Django Settings

Key settings in `chatbot/settings.py`:

- `AUTH_USER_MODEL`: Custom user model with avatar support
- `GEMINI_API_KEY`: Loaded from environment variables
- `TAILWIND_APP_NAME`: Set to 'theme' for Tailwind CSS
- `MEDIA_ROOT`: Directory for user-uploaded files

### API Configuration

The application uses Google Gemini API for AI responses. Make sure to:

1. Get your API key from [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Add it to your `.env` file as `GEMINI_API_KEY`
3. The API is free to use with rate limits

## 🎯 Usage

### User Registration

1. Navigate to `/register/`
2. Fill in username, email, password, and optionally upload an avatar
3. Click "Register" to create your account

### Chatting with the Bot

1. Log in to your account
2. Navigate to `/chat/`
3. Type your message and press Enter or click Send
4. The bot will respond using:
   - Knowledge base (if similar question exists)
   - Google Gemini API (for new questions)
   - Intent recognition (for greetings, etc.)

### Viewing Chat History

1. Navigate to `/history/`
2. View all your previous conversations sorted by date

### Updating Profile

1. Navigate to `/profile/`
2. Update your username, email, or avatar
3. Click "Update Profile"

## 🧠 How It Works

### Response Generation Flow

1. **Intent Detection**: Checks for greetings, farewells, thanks, etc.
2. **Exact Match**: Searches knowledge base for exact question match
3. **Similarity Match**: Uses TF-IDF vectorization to find similar questions (confidence threshold: 0.6)
4. **Gemini Fallback**: If no match found, queries Google Gemini API
5. **Knowledge Caching**: Stores new responses in knowledge base for future use

### Code Generation

The bot can generate code when explicitly requested:
- Detects code request keywords: "write", "create", "generate", "code", etc.
- Extracts programming language from the request
- Generates code using Gemini API
- Formats code for better readability

## 🖼️ Screenshots

### Home Page
![Home Page](media/screenshots/home.png)

### Chat Interface
![Chat Interface](media/screenshots/chat.png)

### Chat History
![Chat History](media/screenshots/history.png)

### User Profile
![User Profile](media/screenshots/profile.png)

### Login Page
![Login Page](media/screenshots/login.png)

### Registration Page
![Registration Page](media/screenshots/register.png)

*Note: Add your actual screenshots to the `media/screenshots/` directory and update the paths above.*

## 🧪 Testing

Run the test suite:

```bash
python manage.py test
```

## 🚀 Deployment

### Production Checklist

1. Set `DEBUG = False` in settings.py
2. Update `ALLOWED_HOSTS` with your domain
3. Set a secure `SECRET_KEY`
4. Use PostgreSQL instead of SQLite
5. Configure static files serving
6. Set up proper media file storage
7. Use environment variables for sensitive data
8. Enable HTTPS

### Environment Variables

```env
DEBUG=False
SECRET_KEY=your-production-secret-key
GEMINI_API_KEY=your-gemini-api-key
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
DATABASE_URL=postgresql://user:password@localhost/dbname
```

## 📝 API Endpoints

- `GET /` - Home page
- `GET /login/` - Login page
- `POST /login/` - Login submission
- `GET /register/` - Registration page
- `POST /register/` - Registration submission
- `GET /chat/` - Chat interface
- `POST /chat/` - Send message (form submission)
- `POST /ajax/chat/` - Send message (AJAX)
- `GET /history/` - Chat history
- `GET /profile/` - User profile
- `POST /profile/` - Update profile
- `GET /logout/` - Logout user
- `GET /admin/` - Django admin panel

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- [Django](https://www.djangoproject.com/) - Web framework
- [Google Gemini](https://ai.google.dev/) - AI API
- [Tailwind CSS](https://tailwindcss.com/) - CSS framework
- [DaisyUI](https://daisyui.com/) - Component library
- [NLTK](https://www.nltk.org/) - Natural Language Toolkit
- [spaCy](https://spacy.io/) - NLP library
- [scikit-learn](https://scikit-learn.org/) - Machine learning library

## 📧 Contact

For questions or support, please open an issue on the repository.

---

**Made with ❤️ using Django and Google Gemini AI**
