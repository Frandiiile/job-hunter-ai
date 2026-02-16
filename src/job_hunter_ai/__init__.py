"""
Job Hunter AI - Automated resume and cover letter generation.

A complete system for automating job applications for Data Engineering roles.
Includes job ingestion, scoring, and LLM-powered document generation.
"""

__version__ = "0.1.0"

# Expose main scoring functions
from .scoring import compute_deterministic_score, compute_hybrid_score

__all__ = [
    "compute_deterministic_score",
    "compute_hybrid_score",
]
