from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import re

def compute_cosine_similarity(text1: str, text2: str) -> float:
    """
    Computes cosine similarity between two text strings using Scikit-Learn TF-IDF Vectorizer.
    Returns float value between 0.0 and 1.0.
    """
    if not text1 or not text2 or not text1.strip() or not text2.strip():
        return 0.0

    # Clean text to remove extra whitespace and non-alphanumeric characters
    t1 = re.sub(r'\s+', ' ', text1).strip().lower()
    t2 = re.sub(r'\s+', ' ', text2).strip().lower()

    if not t1 or not t2:
        return 0.0

    try:
        vectorizer = TfidfVectorizer(stop_words='english')
        tfidf_matrix = vectorizer.fit_transform([t1, t2])
        sim_matrix = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])
        score = float(sim_matrix[0][0])
        # Ensure result stays bounded between 0.0 and 1.0
        return max(0.0, min(1.0, score))
    except Exception:
        return 0.0
