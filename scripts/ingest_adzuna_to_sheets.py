import os
import re
import hashlib
import requests
import gspread
from google.auth import default
from dotenv import load_dotenv

load_dotenv()

# -------------------- Filtering Rules --------------------
SENIOR_NEGATIVE = [
    r"\bsenior\b", r"\blead\b", r"\bstaff\b", r"\bprincipal\b",
    r"\bexpert\b", r"\bconfirmed?\b", r"\bmanager\b", r"\bhead of\b",
]

NO_INTERNSHIPS = [
    r"\bintern\b", r"\binternship\b", r"\bstage\b",
    r"\balternance\b", r"\bapprenticeship\b", r"\bapprenti\b",
    r"\bapprentissage\b", r"\btrainee\b"
]

# Handles: "3 years", "3+ years", "3 ans", "3 années", "au moins 3 ans", "minimum 3 years", "3 ans d'expérience"
YEARS_PATTERNS = [
    r"(\d+)\s*\+?\s*(?:years?|yrs?)\b",
    r"(\d+)\s*\+?\s*(?:ans?|ann[eé]es?)\b",
    r"(?:minimum|at\s+least)\s+(\d+)\s*(?:years?|yrs?)\b",
    r"(?:minimum|au\s+moins)\s+(\d+)\s*(?:ans?|ann[eé]es?)\b",
    r"(\d+)\s*\+?\s*(?:years?|yrs?|ans?|ann[eé]es?)\s+(?:of\s+)?exp[eé]rience\b",
]

def contains_any(text: str, patterns: list[str]) -> bool:
    return any(re.search(p, text, re.IGNORECASE) for p in patterns)

def extract_years_required(text: str):
    for pat in YEARS_PATTERNS:
        m = re.search(pat, text, re.IGNORECASE)
        if m:
            try:
                return int(m.group(1)), m.group(0)
            except ValueError:
                pass
    return None, None

def should_keep(title: str, description: str):
    full = f"{title} {description}".lower()

    # exclude internships/alternance always
    if contains_any(full, NO_INTERNSHIPS):
        return False, None, "Excluded: internship/alternance/apprenticeship detected"

    # exclude senior roles
    if contains_any(full, SENIOR_NEGATIVE):
        return False, None, "Excluded: senior role indicators"

    # years requirement: accept <=2, assume junior if not mentioned
    years, evidence = extract_years_required(full)
    if years is None:
        return True, "", "Kept: no explicit years found (assumed junior)"
    if years <= 2:
        return True, str(years), f"Kept: explicit years <=2 ({evidence})"
    return False, str(years), f"Excluded: explicit years >2 ({evidence})"

# -------------------- Utilities --------------------
def sha1(s: str) -> str:
    return hashlib.sha1(s.encode("utf-8")).hexdigest()

def safe_str(v) -> str:
    if v is None:
        return ""
    return " ".join(str(v).split()).strip()

def pick_city(location: dict) -> str:
    location = location or {}
    display = safe_str(location.get("display_name"))

    for sep in [",", " - ", "-"]:
        if sep in display:
            return safe_str(display.split(sep)[0])

    area = location.get("area")
    if isinstance(area, list) and area:
        return safe_str(area[-1])

    return display  # e.g. "Remote"

# -------------------- Adzuna --------------------
def fetch_adzuna_jobs(country_code: str, query: str, page: int, results_per_page: int):
    app_id = os.environ["ADZUNA_APP_ID"]
    app_key = os.environ["ADZUNA_APP_KEY"]

    url = f"https://api.adzuna.com/v1/api/jobs/{country_code}/search/{page}"
    params = {
        "app_id": app_id,
        "app_key": app_key,
        "what": query,
        "results_per_page": results_per_page,
    }
    r = requests.get(url, params=params, timeout=30)
    r.raise_for_status()
    return r.json().get("results", [])

# -------------------- Google Sheets --------------------
def connect_worksheet():
    spreadsheet_name = os.environ["GOOGLE_SHEETS_SPREADSHEET_NAME"]
    worksheet_name = os.environ.get("GOOGLE_SHEETS_WORKSHEET_NAME", "job_pipeline")

    creds, _ = default(scopes=[
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
    ])
    gc = gspread.authorize(creds)
    sh = gc.open(spreadsheet_name)
    return sh.worksheet(worksheet_name)

def get_headers(ws) -> list[str]:
    headers = ws.row_values(1)
    return [h.strip() for h in headers if h and h.strip()]

def get_existing_job_ids(ws, headers: list[str]) -> set[str]:
    if "job_id" not in headers:
        raise RuntimeError("Sheet must have a 'job_id' column in header row.")
    job_id_col = headers.index("job_id") + 1
    col = ws.col_values(job_id_col)
    return set(v.strip() for v in col[1:] if v and v.strip())

def build_row_values(headers: list[str], data: dict) -> list[str]:
    return [safe_str(data.get(h, "")) for h in headers]

# -------------------- Main --------------------
def main():
    ws = connect_worksheet()
    headers = get_headers(ws)
    existing = get_existing_job_ids(ws, headers)

    # You can later make these configurable via .env
    jobs = fetch_adzuna_jobs(country_code="fr", query="data engineer", page=1, results_per_page=30)

    kept_count = 0
    skipped_count = 0
    new_rows = []

    for job in jobs:
        source = "adzuna"
        job_url = safe_str(job.get("redirect_url") or job.get("adref") or job.get("url"))
        if not job_url:
            skipped_count += 1
            continue

        job_id = sha1(f"{source}|{job_url}")
        if job_id in existing:
            continue

        title = safe_str(job.get("title"))
        description = safe_str(job.get("description"))

        keep, years_guess, reason = should_keep(title, description)
        if not keep:
            skipped_count += 1
            continue

        kept_count += 1

        row_dict = {
            "job_id": job_id,
            "source": source,
            "published_at": safe_str(job.get("created")),
            "country": "FR",
            "city": pick_city(job.get("location")),
            "title": title,
            "company": safe_str((job.get("company") or {}).get("display_name")),
            "contract_ty": safe_str(job.get("contract_type") or ""),
            "url": job_url,
            "description": description,

            # keep status NEW for your workflow
            "status": "NEW",

            # optional columns (safe if they exist; ignored if not)
            "years_required_guess": years_guess,
            "notes": reason,
            # leave these empty for later scripts
            "junior_ok": "",
            "language": "",
            "language_ok": "",
        }

        new_rows.append(build_row_values(headers, row_dict))

    if new_rows:
        ws.append_rows(new_rows, value_input_option="RAW")
        print(f"✅ Added {len(new_rows)} jobs (kept={kept_count}, skipped={skipped_count}).")
    else:
        print(f"ℹ️ No new jobs to add (kept={kept_count}, skipped={skipped_count}).")

if __name__ == "__main__":
    main()
