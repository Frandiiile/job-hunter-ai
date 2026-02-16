# src/job_hunter_ai/scoring.py
"""
Deterministic + hybrid scoring for Data Engineer job matching.

Design goals:
- Explainable deterministic score (fast, stable)
- Optional LLM score blending (hybrid)
- Real "missing skills" by extracting from a curated skill dictionary
  rather than only matching skills already in the profile.

Notes:
- Keep BASE_SKILLS + SKILL_SYNONYMS small at first, then extend as you observe job texts.
- This file has no external deps (pure stdlib).
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Dict, List, Set, Tuple, Optional


# -----------------------------
# Helpers
# -----------------------------
def normalize_text(text: str) -> str:
    return " ".join((text or "").lower().split())


def clamp_int(x: int, lo: int = 0, hi: int = 100) -> int:
    return max(lo, min(hi, int(x)))


# -----------------------------
# Curated skill dictionary (extend over time)
# Keep items normalized lowercase; include common synonyms via SKILL_SYNONYMS.
# -----------------------------
BASE_SKILLS: List[str] = [
    # languages / query
    "python", "sql", "pyspark", "spark", "scala", "java",
    # orchestration
    "airflow", "dagster", "prefect",
    # lakehouse / storage / formats
    "databricks", "delta lake", "iceberg", "hudi",
    # warehouses / databases
    "snowflake", "bigquery", "redshift", "synapse", "postgresql", "mysql", "oracle",
    # streaming / messaging
    "kafka", "spark structured streaming", "flink", "kinesis", "pubsub",
    # transformation / modeling
    "dbt", "data modeling", "star schema", "snowflake schema",
    # testing / quality / governance
    "great expectations", "openlineage", "data lineage", "data contracts", "schema evolution",
    # cloud
    "aws", "gcp", "azure",
    # devops / infra
    "docker", "kubernetes", "terraform", "jenkins", "gitlab ci", "github actions", "ci/cd",
    # observability (optional but valuable)
    "prometheus", "grafana",
    # bi
    "power bi", "looker", "looker studio",
]

# Map "alias pattern" -> canonical skill
SKILL_SYNONYMS: List[Tuple[str, str]] = [
    (r"\bgcp\b", "gcp"),
    (r"\bgoogle cloud\b", "gcp"),
    (r"\bbig query\b", "bigquery"),
    (r"\bbigquery\b", "bigquery"),
    (r"\bgcs\b", "gcp"),  # coarse but useful signal
    (r"\bspark structured streaming\b", "spark structured streaming"),
    (r"\bstructured streaming\b", "spark structured streaming"),
    (r"\bci\/cd\b", "ci/cd"),
    (r"\bcontinuous integration\b", "ci/cd"),
    (r"\bcontinuous deployment\b", "ci/cd"),
    (r"\bgithub\s+actions\b", "github actions"),
    (r"\bgitlab\s+ci\b", "gitlab ci"),
    (r"\bk8s\b", "kubernetes"),
    (r"\beks\b", "kubernetes"),
    (r"\baks\b", "kubernetes"),
    (r"\bterraform\b", "terraform"),
    (r"\bpowerbi\b", "power bi"),
    (r"\blooker\s+studio\b", "looker studio"),
    (r"\bopen lineage\b", "openlineage"),
]


# -----------------------------
# Profile skill extraction
# -----------------------------
def flatten_profile_skills(profile: Dict) -> Set[str]:
    """
    Extract all skills from profile.yaml (technical_stack) into a flat normalized set.
    Supports nested dict structure like:
      technical_stack:
        programming:
          strong: [Python, SQL]
          good: [PySpark]
    """
    skills: Set[str] = set()
    tech_stack = profile.get("technical_stack", {}) or {}

    def add_item(item: str):
        norm = normalize_text(item)
        if norm:
            skills.add(norm)

    def extract_from_section(section):
        if isinstance(section, dict):
            for _, value in section.items():
                extract_from_section(value)
        elif isinstance(section, list):
            for item in section:
                if isinstance(item, str):
                    add_item(item)

    extract_from_section(tech_stack)
    return skills


# -----------------------------
# Job skill extraction
# -----------------------------
def _apply_synonyms(text: str) -> Set[str]:
    found: Set[str] = set()
    for pattern, canonical in SKILL_SYNONYMS:
        if re.search(pattern, text, flags=re.IGNORECASE):
            found.add(normalize_text(canonical))
    return found


def extract_job_skills(job_text: str) -> Set[str]:
    """
    Extract skills from the job text using:
    - curated BASE_SKILLS substring checks (normalized)
    - regex synonyms mapping (SKILL_SYNONYMS)
    """
    text = normalize_text(job_text)
    found: Set[str] = set()

    # Synonyms first (regex)
    found |= _apply_synonyms(text)

    # Direct keyword contains for base skills
    for kw in BASE_SKILLS:
        nkw = normalize_text(kw)
        if nkw and nkw in text:
            found.add(nkw)

    return found


def compute_overlap(job_skills: Set[str], profile_skills: Set[str]) -> Tuple[int, List[str], List[str]]:
    """
    Returns:
      overlap_pct (0-100),
      overlap_skills (sorted),
      missing_skills (sorted)
    """
    if not job_skills:
        return 0, [], []

    overlap = sorted(job_skills & profile_skills)
    missing = sorted(job_skills - profile_skills)
    pct = int(round(100 * (len(overlap) / len(job_skills))))
    return clamp_int(pct), overlap, missing


# -----------------------------
# Bonuses / penalties
# -----------------------------
def architecture_bonus(job_text: str, profile: Dict) -> int:
    text = normalize_text(job_text)
    keywords = profile.get("architecture_experience", []) or []
    matches = 0
    for k in keywords:
        nk = normalize_text(str(k))
        if nk and nk in text:
            matches += 1
    return clamp_int(matches * 5, 0, 20)  # cap +20


def domain_bonus(job_text: str, profile: Dict) -> int:
    text = normalize_text(job_text)
    domains = profile.get("domain_exposure", []) or []
    matches = 0
    for d in domains:
        nd = normalize_text(str(d))
        if nd and nd in text:
            matches += 1
    return clamp_int(matches * 5, 0, 10)  # cap +10


def seniority_penalty(job_text: str, max_years: int = 2) -> int:
    """
    Penalty if job looks senior or explicitly asks for more than max_years.
    Conservative by design: helps ranking when some jobs slip through filtering.
    """
    text = normalize_text(job_text)

    senior_kw = [
        r"\bsenior\b", r"\blead\b", r"\bprincipal\b", r"\bstaff\b",
        r"\bmanager\b", r"\bhead of\b", r"\bconfirmed?\b",
    ]
    if any(re.search(p, text) for p in senior_kw):
        return -20

    year_patterns = [
        r"(\d+)\s*\+?\s*(?:years?|yrs?)\b",
        r"(\d+)\s*\+?\s*(?:ans?|ann[eé]es?)\b",
        r"(?:minimum|at\s+least)\s+(\d+)\s*(?:years?|yrs?)\b",
        r"(?:minimum|au\s+moins)\s+(\d+)\s*(?:ans?|ann[eé]es?)\b",
    ]
    for pat in year_patterns:
        m = re.search(pat, text, flags=re.IGNORECASE)
        if m:
            try:
                years = int(m.group(1))
                if years > max_years:
                    return -20
            except ValueError:
                pass

    return 0


# -----------------------------
# Scoring objects
# -----------------------------
@dataclass
class DeterministicScore:
    job_skills_found: List[str]
    profile_skills_used: List[str]
    skill_overlap_pct: int
    overlap_skills: List[str]
    missing_skills: List[str]
    architecture_bonus: int
    domain_bonus: int
    seniority_penalty: int
    deterministic_score: int


@dataclass
class HybridScore:
    deterministic: DeterministicScore
    llm_score: Optional[int]
    final_score: int
    llm_score_bounds: Optional[Tuple[int, int]]


# -----------------------------
# Core scoring
# -----------------------------
def compute_deterministic_score(profile: Dict, job: Dict) -> DeterministicScore:
    """
    Compute deterministic score for a job based on profile.

    Args:
        profile: Profile dict (must have 'technical_stack')
        job: Job dict (must have 'title' and/or 'description')

    Returns:
        DeterministicScore with detailed breakdown

    Raises:
        ValueError: If required fields are missing or invalid
    """
    # Input validation
    if not isinstance(profile, dict):
        raise ValueError("profile must be a dict")
    if not isinstance(job, dict):
        raise ValueError("job must be a dict")

    job_text = f"{job.get('title', '')}\n{job.get('description', '')}"
    if not job_text.strip():
        raise ValueError("job must have either 'title' or 'description'")

    job_text_norm = normalize_text(job_text)

    profile_skills = flatten_profile_skills(profile)
    job_skills = extract_job_skills(job_text_norm)

    overlap_pct, overlap_list, missing_list = compute_overlap(job_skills, profile_skills)

    arch_b = architecture_bonus(job_text_norm, profile)
    dom_b = domain_bonus(job_text_norm, profile)

    # read max years from profile, fallback to 2
    max_years = 2
    seniority = profile.get("seniority")
    if isinstance(seniority, dict):
        try:
            max_years = int(seniority.get("total_years_experience", 2))
        except Exception:
            max_years = 2

    sen_p = seniority_penalty(job_text_norm, max_years=max_years)

    # Deterministic score: overlap + bonuses + penalty
    det_score = clamp_int(overlap_pct + arch_b + dom_b + sen_p)

    return DeterministicScore(
        job_skills_found=sorted(job_skills),
        profile_skills_used=sorted(profile_skills),
        skill_overlap_pct=overlap_pct,
        overlap_skills=overlap_list,
        missing_skills=missing_list,
        architecture_bonus=arch_b,
        domain_bonus=dom_b,
        seniority_penalty=sen_p,
        deterministic_score=det_score,
    )


def bounded_llm_score(llm_score: int, deterministic_score: int, max_delta: int = 25) -> Tuple[int, Tuple[int, int]]:
    lo = clamp_int(deterministic_score - max_delta)
    hi = clamp_int(deterministic_score + max_delta)
    return clamp_int(llm_score, lo, hi), (lo, hi)


def blend_scores(deterministic_score: int, llm_score: int, weight_llm: float = 0.6) -> int:
    weight_det = 1.0 - float(weight_llm)
    final = (weight_llm * llm_score) + (weight_det * deterministic_score)
    return clamp_int(int(round(final)))


def compute_hybrid_score(
    profile: Dict,
    job: Dict,
    llm_score: Optional[int],
    weight_llm: float = 0.6,
    max_delta: int = 25,
) -> HybridScore:
    det = compute_deterministic_score(profile, job)

    if llm_score is None:
        return HybridScore(
            deterministic=det,
            llm_score=None,
            final_score=det.deterministic_score,
            llm_score_bounds=None,
        )

    bounded, bounds = bounded_llm_score(llm_score, det.deterministic_score, max_delta=max_delta)
    final = blend_scores(det.deterministic_score, bounded, weight_llm=weight_llm)

    return HybridScore(
        deterministic=det,
        llm_score=bounded,
        final_score=final,
        llm_score_bounds=bounds,
    )
