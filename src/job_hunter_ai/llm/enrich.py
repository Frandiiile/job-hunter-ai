import json
from pathlib import Path
import os
from groq import Groq

def load_text(path: str) -> str:
    return Path(path).read_text(encoding="utf-8")

def load_yaml(path: str):
    import yaml
    return yaml.safe_load(Path(path).read_text(encoding="utf-8"))

def call_groq(prompt: str):
    import os
    client = Groq(api_key=os.environ["GROQ_API_KEY"])

    model_name = os.environ.get("GROQ_MODEL", "llama-3.3-70b-versatile")

    resp = client.chat.completions.create(
        model=model_name,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2
    )

    return resp.choices[0].message.content


def build_master_prompt(job_desc: str):
    prof = load_text("profile/profile.yml")
    exp = load_text("profile/experiences.md")
    pro = load_text("profile/projects.md")
    tmpl = load_text("prompts/cv_master_prompt.txt")

    return (
        tmpl
        + "\n\nJOB DESCRIPTION:\n" + job_desc
        + "\n\nPROFILE_YML:\n" + prof
        + "\n\nEXPERIENCES_MD:\n" + exp
        + "\n\nPROJECTS_MD:\n" + pro
    )

def build_cover_prompt(job_desc: str):
    prof = load_text("profile/profile.yml")
    exp = load_text("profile/experiences.md")
    pro = load_text("profile/projects.md")
    tmpl = load_text("prompts/cover_letter_prompt.txt")

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

def generate_master_cv(job_desc: str):
    prompt = build_master_prompt(job_desc)
    raw = call_groq(prompt)
    cleaned = clean_json_output(raw)
    try:
        return json.loads(cleaned)
    except Exception as e:
        raise ValueError("Groq did not return valid JSON.\nCleaned output:\n" + cleaned)


def generate_cover_letter(job_desc: str):
    prompt = build_cover_prompt(job_desc)
    raw = call_groq(prompt)
    cleaned = clean_json_output(raw)
    try:
        return json.loads(cleaned)
    except Exception as e:
        raise ValueError("Groq did not return valid JSON.\nCleaned output:\n" + cleaned)

def compress_to_one_page(master_json, job_desc):
    prompt = load_text("prompts/cv_one_page_prompt.txt")
    prompt = prompt.replace("<<MASTER_JSON>>", json.dumps(master_json, indent=2))
    prompt = prompt.replace("<<JOB_DESCRIPTION>>", job_desc)

    raw = call_groq(prompt)
    cleaned = clean_json_output(raw)

    return json.loads(cleaned)


