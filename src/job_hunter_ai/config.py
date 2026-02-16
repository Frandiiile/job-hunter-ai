"""
Configuration module for Job Hunter AI.

All tunable parameters, API keys, and environment-specific settings.
"""

import os
from pathlib import Path
from typing import Optional

# =====================================
# Project Paths
# =====================================
PROJECT_ROOT = Path(__file__).parent.parent.parent
PROFILE_DIR = PROJECT_ROOT / "profile"
PROMPTS_DIR = PROJECT_ROOT / "prompts"
TEMPLATES_DIR = PROJECT_ROOT / "templates"
BUILD_DIR = PROJECT_ROOT / "build"

# =====================================
# LLM Configuration
# =====================================
GROQ_API_KEY: Optional[str] = os.environ.get("GROQ_API_KEY")
GROQ_MODEL: str = os.environ.get("GROQ_MODEL", "llama-3.3-70b-versatile")
GROQ_TEMPERATURE: float = float(os.environ.get("GROQ_TEMPERATURE", "0.2"))
GROQ_TIMEOUT: int = int(os.environ.get("GROQ_TIMEOUT", "60"))

# =====================================
# Scoring Configuration
# =====================================
# Hybrid score blending
WEIGHT_LLM: float = 0.6  # LLM weight in final score
WEIGHT_DETERMINISTIC: float = 0.4  # Deterministic weight

# LLM score bounding (prevent wild deviations)
MAX_LLM_DELTA: int = 25  # Maximum +/- from deterministic score

# Bonuses
MAX_ARCHITECTURE_BONUS: int = 20
MAX_DOMAIN_BONUS: int = 10

# Penalties
SENIORITY_PENALTY: int = -20

# Default candidate max experience (can be overridden from profile)
DEFAULT_MAX_YEARS: int = 2

# =====================================
# Google Sheets Configuration
# =====================================
GOOGLE_SHEETS_SPREADSHEET_NAME: str = os.environ.get(
    "GOOGLE_SHEETS_SPREADSHEET_NAME", "job_pipeline"
)
GOOGLE_SHEETS_WORKSHEET_NAME: str = os.environ.get(
    "GOOGLE_SHEETS_WORKSHEET_NAME", "daily_jobs"
)

# =====================================
# Adzuna API Configuration
# =====================================
ADZUNA_APP_ID: Optional[str] = os.environ.get("ADZUNA_APP_ID")
ADZUNA_APP_KEY: Optional[str] = os.environ.get("ADZUNA_APP_KEY")

# =====================================
# Google Drive Configuration (Optional)
# =====================================
GOOGLE_DRIVE_FOLDER_ID: Optional[str] = os.environ.get("GOOGLE_DRIVE_FOLDER_ID")
GOOGLE_CREDENTIALS_PATH: Optional[str] = os.environ.get("GOOGLE_CREDENTIALS_PATH")

# =====================================
# Validation
# =====================================
def validate_config():
    """Validate critical configuration before running."""
    errors = []

    if not GROQ_API_KEY:
        errors.append("GROQ_API_KEY not set in environment")

    if not PROFILE_DIR.exists():
        errors.append(f"Profile directory not found: {PROFILE_DIR}")

    if not PROMPTS_DIR.exists():
        errors.append(f"Prompts directory not found: {PROMPTS_DIR}")

    if not TEMPLATES_DIR.exists():
        errors.append(f"Templates directory not found: {TEMPLATES_DIR}")

    if errors:
        raise ValueError("Configuration errors:\n" + "\n".join(f"  - {e}" for e in errors))

# =====================================
# Path helpers
# =====================================
def get_profile_path(filename: str) -> Path:
    """Get full path to profile file."""
    return PROFILE_DIR / filename

def get_prompt_path(filename: str) -> Path:
    """Get full path to prompt file."""
    return PROMPTS_DIR / filename

def get_template_path(filename: str) -> Path:
    """Get full path to template file."""
    return TEMPLATES_DIR / filename

def get_build_path(job_id: str) -> Path:
    """Get full path to job build directory."""
    path = BUILD_DIR / "jobs" / job_id
    path.mkdir(parents=True, exist_ok=True)
    return path
