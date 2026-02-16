from pathlib import Path
from src.job_hunter_ai.llm.enrich import generate_master_cv, generate_cover_letter, compress_to_one_page
from src.job_hunter_ai.latex.render_template import render_cv_template, render_cover_template

def load_template(p): return Path(p).read_text(encoding="utf-8")

def main():
    job = {
        "title": "Junior Data Engineer",
        "description": "We want Airflow, Python, GCP, CI/CD, and cloud pipelines..."
    }

    print("Generating LLM content...")
    cv_master = generate_master_cv(job["description"])
    cv_one_page = compress_to_one_page(cv_master, job["description"])
    cl_json = generate_cover_letter(job["description"])

    cv_template = load_template("templates/cv_template.tex")
    cover_template = load_template("templates/cover_template.tex")

    cv_output = render_cv_template(cv_template, job, cv_one_page)
    cl_output = render_cover_template(cover_template, job, cl_json)

    out = Path("generated_test")
    out.mkdir(exist_ok=True)

    (out/"cv_test.tex").write_text(cv_output, encoding="utf-8")
    (out/"cover_test.tex").write_text(cl_output, encoding="utf-8")

    print("✅ Done! Check generated_test/ folder.")

if __name__ == "__main__":
    main()
