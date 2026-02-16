import yaml
from src.job_hunter_ai.scoring import compute_hybrid_score
from src.job_hunter_ai.llm.enrich import enrich_with_llm


with open("profile/profile.yml", "r", encoding="utf-8") as f:
    profile = yaml.safe_load(f)

with open("profile/experiences.md", "r", encoding="utf-8") as f:
    experiences_md = f.read()

with open("profile/projects.md", "r", encoding="utf-8") as f:
    projects_md = f.read()

job = {
    "title": "Cloud Data Engineer",
    "description": """
    We are looking for a Data Engineer with strong Python, SQL,
    Airflow, Snowflake, and Terraform experience.
    Experience with Kafka and streaming pipelines is a plus.
    """
}

# Step 1 — Deterministic
deterministic = compute_hybrid_score(profile, job, llm_score=None)
print("Deterministic score:", deterministic.final_score)

# Step 2 — LLM enrichment
llm_output = enrich_with_llm(profile, experiences_md, projects_md, job, deterministic.final_score)

print("LLM score:", llm_output["llm_score"])

# Step 3 — Hybrid blend
hybrid = compute_hybrid_score(profile, job, llm_score=llm_output["llm_score"])

print("Final hybrid score:", hybrid.final_score)
print("Reasoning:", llm_output["fit_reasoning"])
