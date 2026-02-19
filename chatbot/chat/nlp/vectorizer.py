from typing import List, Tuple
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


class ChatbotVectorizer:
    """
    TF-IDF based vectorizer for chatbot question matching
    """

    def __init__(self, questions: List[str]):
        if not questions:
            raise ValueError("ChatbotVectorizer requires at least one question")

        # Questions are already cleaned, just filter empties
        self.questions = [q for q in questions if q and q.strip()]

        if not self.questions:
            raise ValueError("All questions are empty")

        self.vectorizer = TfidfVectorizer(
            ngram_range=(1, 2),
            min_df=1,
            max_df=0.9,
            sublinear_tf=True
        )

        self.question_vectors = self.vectorizer.fit_transform(self.questions)

    def find_best_match(self, user_input: str) -> Tuple[int, float]:
        """
        Return (best_index, confidence_score)
        User input should already be cleaned before calling this
        """

        if not isinstance(user_input, str) or not user_input.strip():
            return -1, 0.0

        user_vector = self.vectorizer.transform([user_input])

        similarities = cosine_similarity(
            user_vector, self.question_vectors
        )[0]

        best_index = int(similarities.argmax())
        best_score = float(similarities[best_index])

        return best_index, best_score