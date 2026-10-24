import logging
from typing import Optional
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

logger = logging.getLogger(__name__)

_model: Optional[object] = None
_model_load_attempted = False


def _get_embedding_model():
    """Lazily load SentenceTransformer model to save startup memory on free-tier containers."""
    global _model, _model_load_attempted
    if _model is not None:
        return _model
    if _model_load_attempted:
        return None

    _model_load_attempted = True
    try:
        from sentence_transformers import SentenceTransformer
        logger.info("Loading SentenceTransformer model 'all-MiniLM-L6-v2'...")
        _model = SentenceTransformer('all-MiniLM-L6-v2')
        logger.info("SentenceTransformer loaded successfully.")
        return _model
    except Exception as e:
        logger.warning(f"Could not load SentenceTransformer ({e}). Falling back to TF-IDF similarity.")
        _model = None
        return None


def skill_overlap_score(resume_skills, jd_skills):
    resume_set = set(resume_skills)
    jd_set = set(jd_skills)

    if not jd_set:
        return 0.0

    overlap = resume_set.intersection(jd_set)
    return float(len(overlap) / len(jd_set))


def category_overlap_score(resume_categories, jd_categories):
    resume_cat = set(resume_categories.keys())
    jd_cat = set(jd_categories.keys())

    if not jd_cat:
        return 0.0

    overlap = resume_cat.intersection(jd_cat)
    return float(len(overlap) / len(jd_cat))


def tfidf_similarity(resume_text, jd_text):
    if not (resume_text or "").strip() or not (jd_text or "").strip():
        return 0.0
    try:
        vectorizer = TfidfVectorizer(stop_words='english')
        vectors = vectorizer.fit_transform([resume_text, jd_text])
        similarity = cosine_similarity(vectors[0:1], vectors[1:2])[0][0]
        return float(similarity)
    except Exception as e:
        logger.warning(f"TF-IDF similarity calculation error: {e}")
        return 0.0


def semantic_similarity(resume_text, jd_text):
    if not (resume_text or "").strip() or not (jd_text or "").strip():
        return 0.0

    model = _get_embedding_model()
    if model is None:
        # Fallback to TF-IDF if embedding model is not available or low memory
        return tfidf_similarity(resume_text, jd_text)

    try:
        embeddings = model.encode([resume_text, jd_text])
        norm0 = np.linalg.norm(embeddings[0])
        norm1 = np.linalg.norm(embeddings[1])
        if norm0 == 0 or norm1 == 0:
            return 0.0
        sim = np.dot(embeddings[0], embeddings[1]) / (norm0 * norm1)
        return float(sim)
    except Exception as e:
        logger.warning(f"Semantic similarity failed ({e}); falling back to TF-IDF.")
        return tfidf_similarity(resume_text, jd_text)


def compute_final_score(skill_score, category_score, tfidf_score, semantic_score):
    final = (
        0.3 * skill_score +
        0.2 * category_score +
        0.25 * tfidf_score +
        0.25 * semantic_score
    )
    return round(float(final * 100), 2)

