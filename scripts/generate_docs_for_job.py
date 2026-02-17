from dotenv import load_dotenv
load_dotenv()

import json
import os
from pathlib import Path
from src.job_hunter_ai.latex.render_template import render_template
from src.job_hunter_ai.drive.upload import upload_to_drive
from src.job_hunter_ai.llm.enrich import enrich_with_llm
from src.job_hunter_ai.scoring import compute_hybrid_score
import yaml

def main():
    # Dummy job for testing
    job = {
        "title": "Data Engineer",
        "company": "ExampleCorp",
        "description": "We are looking for a Data Engineer with Airflow, Python, AWS...",
        "id": "test-job-123"
    }

    # Load profile + blocks
    profile = yaml.safe_load(Path("profile/profile.yml").read_text())
    experiences_md = Path("profile/experiences.md").read_text()
    projects_md = Path("profile/projects.md").read_text()

    # Step 1: compute score
    deterministic = compute_hybrid_score(profile, job,llm_score=None)

    # Step 2: LLM tailoring
    llm_output = enrich_with_llm(
        profile, experiences_md, projects_md,
        job, deterministic.final_score
    )

    job_id = job["id"]
    out_dir = Path(f"build/jobs/{job_id}")
    out_dir.mkdir(parents=True, exist_ok=True)

    # Step 3: render CV and cover letter TEX files
    cv_tex = Path("templates/cv_template.tex").read_text()
    cover_tex = Path("templates/cover_template.tex").read_text()

    filled_cv = render_template(cv_tex, job, llm_output)
    filled_cover = render_template(cover_tex, job, llm_output)

    cv_path = out_dir / "cv.tex"
    cover_path = out_dir / "cover_letter.tex"

    cv_path.write_text(filled_cv, encoding="utf-8")
    cover_path.write_text(filled_cover, encoding="utf-8")

    print(f"✔ Generated LaTeX CV: {cv_path}")
    print(f"✔ Generated LaTeX Cover Letter: {cover_path}")

    # Step 4: upload files to Drive (optional)
    cv_drive_url = upload_to_drive(cv_path)
    cover_drive_url = upload_to_drive(cover_path)

    print("Drive links:")
    print("CV:", cv_drive_url)
    print("Cover Letter:", cover_drive_url)

if __name__ == "__main__":
    main()
