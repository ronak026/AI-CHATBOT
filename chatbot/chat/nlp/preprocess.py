import re
from typing import Set

try:
    import nltk
    from nltk.corpus import stopwords
    from nltk.tokenize import word_tokenize

    _STOP_WORDS: Set[str] = set(stopwords.words("english"))
    # Add articles to stopwords for better matching
    _STOP_WORDS.update(['a', 'an', 'the'])
    _TOKENIZER_AVAILABLE = True
except Exception:
    # Fallback if NLTK data is missing (production safe)
    _STOP_WORDS = {
        'a', 'an', 'the', 'is', 'are', 'was', 'were', 'in', 'on', 'at',
        'to', 'for', 'of', 'with', 'from', 'by', 'as', 'or', 'and'
    }
    _TOKENIZER_AVAILABLE = False


def clean_text(text: str) -> str:
    """
    Clean and preprocess user input text safely.

    - Lowercases text
    - Removes special characters
    - Tokenizes text
    - Removes stopwords (including articles)
    """

    if not isinstance(text, str) or not text.strip():
        return ""

    text = text.lower().strip()

    # Keep letters and numbers (useful for dates, versions, etc.)
    text = re.sub(r"[^a-z0-9\s]", " ", text)

    if _TOKENIZER_AVAILABLE:
        try:
            tokens = word_tokenize(text)
        except Exception:
            tokens = text.split()
    else:
        tokens = text.split()

    # Remove stopwords and empty tokens
    tokens = [word for word in tokens if word and word not in _STOP_WORDS]

    return " ".join(tokens)