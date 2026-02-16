from pathlib import Path
import yaml
from src.job_hunter_ai.latex.render_template import render_template

def load_template(path):
    return Path(path).read_text(encoding="utf-8")

def main():
    # --- Load templates (your real ones) ---
    cv_template = load_template("templates/cv_template.tex")
    cover_template = load_template("templates/cover_template.tex")

    # --- Fake Job ---
    job = {
        "title": "Junior Data Engineer",
        "company": "TestCorp"
    }

    # --- Fake minimal LLM output ---
    llm_output = {
        "profile_summary": "Strong Data Engineer with cloud, Python, and Airflow experience.",

        "experience": {
            "socotec": [
                "Built pipelines in AWS & Databricks.",
                "Optimized SQL queries for finance.",
                "Implemented CI/CD processes.",
                "Reduced PROD incidents by 70%."
            ],
            "leyton": [
                "Developed ELT pipelines with PySpark.",
                "Integrated APIs and CRM data sources.",
                "Designed Bronze/Silver/Gold models."
            ],
            "bourse": [
                "Automated financial reporting in SQL."
            ],
            "wafa": [
                "Produced portfolio risk dashboards."
            ]
        },

        "projects": [
            "Built AskMyData (NL → SQL using FastAPI + pgvector).",
            "Implemented Snowflake + DBT pipelines."
        ],

        "cover_letter": {
            "intro": "I am applying for the Data Engineer role at TestCorp.",
            "body_1": "I have strong experience with cloud data engineering.",
            "body_2": "My background in Airflow and Spark matches your needs.",
            "body_3": "I am motivated to bring impact and high-quality engineering.",
            "outro": "I would be happy to discuss further in an interview."
        }
    }

    # --- Render documents ---
    cv_filled = render_template(cv_template, job, llm_output)
    cover_filled = render_template(cover_template, job, llm_output)

    # --- Output directory ---
    out_dir = Path("generated_test")
    out_dir.mkdir(exist_ok=True)

    (out_dir / "cv_test.tex").write_text(cv_filled, encoding="utf-8")
    (out_dir / "cover_test.tex").write_text(cover_filled, encoding="utf-8")

    print("✅ Test LaTeX files generated successfully!")
    print("➡ Check folder: generated_test/")
    print("➡ Files: cv_test.tex, cover_test.tex")


if __name__ == "__main__":
    main()
