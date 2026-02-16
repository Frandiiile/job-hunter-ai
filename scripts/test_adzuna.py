import os
import hashlib
import requests

APP_ID = os.environ["ADZUNA_APP_ID"]
APP_KEY = os.environ["ADZUNA_APP_KEY"]

def sha1(s: str) -> str:
    return hashlib.sha1(s.encode("utf-8")).hexdigest()

def safe_str(v) -> str:
    if v is None:
        return ""
    return " ".join(str(v).split()).strip()

def pick_city(location: dict) -> str:
    location = location or {}
    display = safe_str(location.get("display_name"))
    if "," in display:
        return safe_str(display.split(",")[0])
    area = location.get("area")
    if isinstance(area, list) and area:
        return safe_str(area[-1])
    return display

url = "https://api.adzuna.com/v1/api/jobs/fr/search/1"
params = {
    "app_id": APP_ID,
    "app_key": APP_KEY,
    "what": "data engineer",
    "results_per_page": 3,
}

r = requests.get(url, params=params, timeout=30)
r.raise_for_status()
data = r.json()

jobs = data.get("results", [])

for job in jobs:
    source = "adzuna"
    url = safe_str(job.get("redirect_url") or job.get("adref") or job.get("url"))
    job_id = sha1(f"{source}|{url}")

    normalized = {
        "job_id": job_id,
        "source": source,
        "published_at": safe_str(job.get("created")),
        "country": "FR",
        "city": pick_city(job.get("location")),
        "title": safe_str(job.get("title")),
        "company": safe_str((job.get("company") or {}).get("display_name")),
        "contract_ty": safe_str(job.get("contract_type")),
        "url": url,
        "description": safe_str(job.get("description")),
        "status": "NEW",
    }

    print("\n--- Normalized Job ---")
    for k, v in normalized.items():
        print(f"{k}: {v}")
