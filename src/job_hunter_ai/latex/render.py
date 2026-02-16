"""
DEPRECATED: This module is kept for backward compatibility.
Please use render_template.py directly.

Legacy wrapper around render_template module.
"""

from __future__ import annotations
from pathlib import Path
from typing import Dict, List

# Import canonical implementations
from .render_template import (
    latex_escape as escape_latex,
    bullets_to_latex as bullets_to_items,
    render_cv_template,
    render_cover_template,
)

# Keep old constant for backward compatibility
LATEX_SPECIALS = {
    "\\": r"\textbackslash{}",
    "&": r"\&",
    "%": r"\%",
    "$": r"\$",
    "#": r"\#",
    "_": r"\_",
    "{": r"\{",
    "}": r"\}",
    "~": r"\textasciitilde{}",
    "^": r"\textasciicircum{}",
}


def projects_to_items(project_items: List[Dict[str, str]]) -> str:
    """
    DEPRECATED: Use render_template.render_cv_template instead.

    Expect list of dicts like:
    {"name": "AskMyData (NL → SQL)", "bullet": "Developed ... (FastAPI, pgvector, Docker)"}
    """
    lines = []
    for p in project_items:
        name = escape_latex(p.get("name", "").strip())
        bullet = escape_latex(p.get("bullet", "").strip())
        if name and bullet:
            lines.append(r"\item \textbf{" + name + r".} " + bullet)
        elif bullet:
            lines.append(r"\item " + bullet)
    return "\n\n".join(lines)


def render_template(template_path: str, replacements: Dict[str, str]) -> str:
    """
    DEPRECATED: Use render_template.render_cv_template or render_cover_template.

    Legacy generic template renderer.
    """
    tex = Path(template_path).read_text(encoding="utf-8")
    for key, value in replacements.items():
        tex = tex.replace(key, value)
    return tex


def render_cv(
    template_path: str,
    profile_summary: str,
    socotec_bullets: List[str],
    leyton_bullets: List[str],
    bourse_bullet: str,
    wafa_bullet: str,
    project_items: List[Dict[str, str]],
) -> str:
    """
    DEPRECATED: Use render_template.render_cv_template instead.
    """
    replacements = {
        "%%PROFILE_SUMMARY%%": escape_latex(profile_summary.strip()),
        "%%SOCOTEC_BULLETS%%": bullets_to_items(socotec_bullets),
        "%%LEYTON_BULLETS%%": bullets_to_items(leyton_bullets),
        "%%BOURSE_BULLET%%": bullets_to_items([bourse_bullet]),
        "%%WAFA_BULLET%%": bullets_to_items([wafa_bullet]),
        "%%PROJECT_ITEMS%%": projects_to_items(project_items),
    }
    return render_template(template_path, replacements)


def render_cover(
    template_path: str,
    job_title: str,
    company: str,
    cover_body: str,
) -> str:
    """
    DEPRECATED: Use render_template.render_cover_template instead.
    """
    replacements = {
        "%%JOB_TITLE%%": escape_latex(job_title.strip()),
        "%%COMPANY%%": escape_latex((company or "").strip()),
        "%%COVER_BODY%%": escape_latex(cover_body.strip()).replace("\n", r"\\"),
    }
    return render_template(template_path, replacements)
