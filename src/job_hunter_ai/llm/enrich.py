import json
from pathlib import Path
from typing import Dict, Any

# Import from groq_client module
from .groq_client import call_groq, GroqClientError

# Import config for file paths
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from job_hunter_ai.config import (
    get_profile_path,
    get_prompt_path,
)

def load_text(path: str) -> str:
    return Path(path).read_text(encoding="utf-8")

def load_yaml(path: str):
    import yaml
    return yaml.safe_load(Path(path).read_text(encoding="utf-8"))


def build_master_prompt(job_desc: str):
    prof = get_profile_path("profile.yml").read_text(encoding="utf-8")
    exp = get_profile_path("experiences.md").read_text(encoding="utf-8")
    pro = get_profile_path("projects.md").read_text(encoding="utf-8")
    tmpl = get_prompt_path("cv_master_prompt.txt").read_text(encoding="utf-8")

    return (
        tmpl
        + "\n\nJOB DESCRIPTION:\n" + job_desc
        + "\n\nPROFILE_YML:\n" + prof
        + "\n\nEXPERIENCES_MD:\n" + exp
        + "\n\nPROJECTS_MD:\n" + pro
    )

def build_cover_prompt(job_desc: str):
    prof = get_profile_path("profile.yml").read_text(encoding="utf-8")
    exp = get_profile_path("experiences.md").read_text(encoding="utf-8")
    pro = get_profile_path("projects.md").read_text(encoding="utf-8")
    tmpl = get_prompt_path("cover_letter_prompt.txt").read_text(encoding="utf-8")

    return (
        tmpl
        + "\n\nJOB DESCRIPTION:\n" + job_desc
        + "\n\nPROFILE_YML:\n" + prof
        + "\n\nEXPERIENCES_MD:\n" + exp
        + "\n\nPROJECTS_MD:\n" + pro
    )

def clean_json_output(raw: str) -> str:
    raw = raw.strip()

    # Remove ```json ... ``` wrappers if present
    if raw.startswith("```"):
        raw = raw.strip("`")
        raw = raw.replace("json", "", 1).strip()

    return raw

def generate_master_cv(job_desc: str) -> Dict[str, Any]:
    """
    Generate master CV JSON from job description.

    Raises:
        GroqClientError: If LLM call fails
        ValueError: If LLM output is not valid JSON
    """
    try:
        prompt = build_master_prompt(job_desc)
        raw = call_groq(prompt)
        cleaned = clean_json_output(raw)
        return json.loads(cleaned)
    except json.JSONDecodeError as e:
        raise ValueError(
            f"Groq did not return valid JSON. Error: {str(e)}\nCleaned output:\n{cleaned}"
        ) from e
    except GroqClientError:
        raise  # Re-raise Groq errors as-is


def generate_cover_letter(job_desc: str) -> Dict[str, Any]:
    """
    Generate cover letter JSON from job description.

    Raises:
        GroqClientError: If LLM call fails
        ValueError: If LLM output is not valid JSON
    """
    try:
        prompt = build_cover_prompt(job_desc)
        raw = call_groq(prompt)
        cleaned = clean_json_output(raw)
        return json.loads(cleaned)
    except json.JSONDecodeError as e:
        raise ValueError(
            f"Groq did not return valid JSON. Error: {str(e)}\nCleaned output:\n{cleaned}"
        ) from e
    except GroqClientError:
        raise  # Re-raise Groq errors as-is

def compress_to_one_page(master_json, job_desc):
    prompt = get_prompt_path("cv_one_page_prompt.txt").read_text(encoding="utf-8")
    prompt = prompt.replace("<<MASTER_JSON>>", json.dumps(master_json, indent=2))
    prompt = prompt.replace("<<JOB_DESCRIPTION>>", job_desc)

    raw = call_groq(prompt)
    cleaned = clean_json_output(raw)

    return json.loads(cleaned)


def enrich_with_llm(
    profile: Dict[str, Any],
    experiences_md: str,
    projects_md: str,
    job: Dict[str, Any],
    deterministic_score: int,
) -> Dict[str, Any]:
    """
    Enrich job application with LLM-generated content.

    This is the high-level function that orchestrates the full LLM pipeline:
    1. Generate master CV
    2. Compress to one page
    3. Generate cover letter
    4. Add metadata

    Args:
        profile: Profile dict from profile.yml
        experiences_md: Raw markdown of experiences
        projects_md: Raw markdown of projects
        job: Job dict with 'title' and 'description'
        deterministic_score: Pre-computed deterministic score

    Returns:
        Dict containing:
        - summary: Profile summary
        - experience: Dict of experience bullets per company
        - projects: List of selected projects
        - cover_letter: Dict of cover letter sections
        - skills_focus: List of skills to emphasize
        - fit_reasoning: LLM's reasoning about fit
        - llm_score: LLM's score (0-100)
        - deterministic_score: Passed-through deterministic score

    Raises:
        GroqClientError: If LLM calls fail
        ValueError: If LLM outputs invalid JSON
    """
    job_desc = f"{job.get('title', '')}\n{job.get('description', '')}"

    # Step 1: Generate master CV
    master_cv = generate_master_cv(job_desc)

    # Step 2: Compress to one page
    one_page_cv = compress_to_one_page(master_cv, job_desc)

    # Step 3: Generate cover letter
    cover_letter = generate_cover_letter(job_desc)

    # Step 4: Combine outputs with metadata
    result = {
        "summary": one_page_cv.get("summary", ""),
        "experience": one_page_cv.get("experience", {}),
        "projects": one_page_cv.get("projects", []),
        "cover_letter": cover_letter,
        "skills_focus": one_page_cv.get("skills_focus", []),
        "fit_reasoning": one_page_cv.get("fit_reasoning", ""),
        "llm_score": one_page_cv.get("llm_score", deterministic_score),
        "deterministic_score": deterministic_score,
    }

    return result
