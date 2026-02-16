import re
from typing import Dict, Any, List

LATEX_SPECIAL_CHARS = {
    "&": r"\&",
    "%": r"\%",
    "$": r"\$",
    "#": r"\#",
    "_": r"\_",
    "{": r"\{",
    "}": r"\}",
    "~": r"\textasciitilde{}",
    "^": r"\textasciicircum{}",
    "\\": r"\textbackslash{}",
}

def latex_escape(text: str) -> str:
    if not text:
        return ""
    for char, escaped in LATEX_SPECIAL_CHARS.items():
        text = text.replace(char, escaped)
    return text

def bullets_to_latex(bullets: List[str]) -> str:
    return "\n".join([f"  \\item {latex_escape(b)}" for b in bullets])


# ----------------------------------------------------------
#               CV RENDERER  (uses experience + projects)
# ----------------------------------------------------------
def render_cv_template(template_str: str, job: Dict[str, Any], cv_json: Dict[str, Any]) -> str:

    summary = latex_escape(cv_json.get("summary", ""))

    soco = bullets_to_latex(cv_json["experience"]["socotec"])
    ley  = bullets_to_latex(cv_json["experience"]["leyton"])
    bou  = bullets_to_latex(cv_json["experience"]["bourse"])
    waf  = bullets_to_latex(cv_json["experience"]["wafa"])

    proj_blocks = []
    for p in cv_json["projects"]:
        name = latex_escape(p.get("name", ""))
        one = latex_escape(p.get("one_liner", ""))

        block = f"\\item \\textbf{{{name}}}: {one}\n"

        # Support both compressed ("bullet") and detailed ("bullets") formats
        bullets = []

        if "bullets" in p:
            bullets = p["bullets"]
        elif "bullet" in p:
            bullets = [p["bullet"]]   # wrap single bullet

        if bullets:
            block += "  \\begin{itemize}\n"
            for b in bullets:
                block += f"    \\item {latex_escape(b)}\n"
            block += "  \\end{itemize}\n"

        proj_blocks.append(block)

    projects_final = "\n".join(proj_blocks)


    replacements = {
        "%%PROFILE_SUMMARY%%": summary,
        "%%SOCOTEC_BULLETS%%": soco,
        "%%LEYTON_BULLETS%%": ley,
        "%%BOURSE_BULLETS%%": bou,
        "%%WAFA_BULLETS%%": waf,
        "%%PROJECTS_BULLETS%%": projects_final,
        "%%JOB_TITLE%%": latex_escape(job.get("title", "")),
    }

    for key, val in replacements.items():
        template_str = template_str.replace(key, val)

    return template_str


# ----------------------------------------------------------
#             COVER LETTER RENDERER
# ----------------------------------------------------------
def render_cover_template(template_str: str, job: Dict[str, Any], cl_json: Dict[str, Any]) -> str:

    replacements = {
        "%%JOB_TITLE%%": latex_escape(job.get("title", "")),
        "%%CL_INTRO%%": latex_escape(cl_json.get("intro", "")),
        "%%CL_BODY_1%%": latex_escape(cl_json.get("body_1", "")),
        "%%CL_BODY_2%%": latex_escape(cl_json.get("body_2", "")),
        "%%CL_BODY_3%%": latex_escape(cl_json.get("body_3", "")),
        "%%CL_OUTRO%%": latex_escape(cl_json.get("outro", "")),
    }

    for key, val in replacements.items():
        template_str = template_str.replace(key, val)

    return template_str


# ----------------------------------------------------------
#             GENERIC TEMPLATE RENDERER (Auto-detect)
# ----------------------------------------------------------
def render_template(
    template_str: str,
    job: Dict[str, Any],
    llm_output: Dict[str, Any],
) -> str:
    """
    Generic template renderer that auto-detects CV vs Cover Letter.

    This function provides backward compatibility with scripts that use
    a generic render_template interface.

    Args:
        template_str: LaTeX template string
        job: Job dict with at least 'title'
        llm_output: LLM output dict

    Returns:
        Rendered LaTeX string

    Note:
        Detection logic:
        - If llm_output has 'cover_letter' key -> render as cover letter
        - Otherwise -> render as CV
    """
    # Auto-detect template type based on llm_output structure
    if "cover_letter" in llm_output:
        # It's a cover letter
        return render_cover_template(template_str, job, llm_output["cover_letter"])
    else:
        # It's a CV
        return render_cv_template(template_str, job, llm_output)
