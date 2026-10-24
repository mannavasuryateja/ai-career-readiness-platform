"""Utility functions for resume service - stub for development"""
from typing import Dict, List, Any
import logging

logger = logging.getLogger(__name__)


def normalize_text(text: str) -> str:
    """Normalize text."""
    return text.lower().strip()


def extract_keywords(text: str) -> List[str]:
    """Extract keywords from text."""
    words = text.split()
    return [w for w in words if len(w) > 3]


def calculate_similarity(text1: str, text2: str) -> float:
    """Calculate text similarity."""
    return 0.5
