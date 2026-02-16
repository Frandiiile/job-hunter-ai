import os
import re
import gspread
from google.auth import default
from dotenv import load_dotenv

load_dotenv()

# ---------- Config ----------
SENIOR_NEGATIVE = [
    r"\bsenior\b", r"\blead\b", r"\bstaff\b", r"\bprincipal\b",
    r"\bexpert\b", r"\bconfirmed?\b", r"\bmanager\b", r"\bhead of\b",
]

# exclude internships / alternance / apprenticeships
NO_INTERNSHIPS = [
    r"\bintern\b", r"\binternship\b", r"\bstage\b",
    r"\balternance\b", r"\bapprenticeship\b", r"\bapprenti\b", r"\bapprentissage\b",
    r"\btrainee\b"
]

# positive junior hints (not strictly required, but helps scoring/notes)
JUNIOR_POSITIVE = [
    r"\bjunior\b", r"\bentry[- ]level\b", r"\bgraduate\b",
    r"\bd[ée]butant\b", r"\bpremi[eè]re exp[eé]rience\b",
    r"\b0\s*[-–]\s*2\b", r"\b0\s*to\s*2\b",
]

# detect explicit years requirement (we accept <=2; otherwise reject)
YEARS_PATTERNS = [
    # English: 3 years, 3+ years, 3 yrs
    r"(\d+)\s*\+?\s*(?:years?|yrs?)\b",

    # French: 3 ans, 3 années
    r"(\d+)\s*\+?\s*(?:ans?|ann[eé]es?)\b",

    # With experience wording
    r"(\d+)\s*\+?\s*(?:years?|yrs?|ans?|ann[eé]es?)\s+(?:of\s+)?exp[eé]rience",

    # minimum / at least (English)
    r"(?:minimum|at\s+least)\s+(\d+)\s*(?:years?|yrs?)",

    # minimum / au moins (French)
    r"(?:minimum|au\s+moins)\s+(\d+)\s*(?:ans?|ann[eé]es?)",
]


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

def norm_text(s: str) -> str:
    return " ".join((s or "").lower().split())

def contains_any(text: str, patterns: list[str]) -> bool:
    return any(re.search(p, text, re.IGNORECASE) for p in patterns)

def extract_years_required(text: str):
    """Return (years:int|None, evidence:str|None)."""
    for pat in YEARS_PATTERNS:
        m = re.search(pat, text, re.IGNORECASE)
        if m:
            try:
                years = int(m.group(1))
                evidence = m.group(0)
                return years, evidence
            except ValueError:
                continue
    return None, None

def detect_language(text: str):
    # lightweight keyword detection
    has_fr = bool(re.search(r"\bfran[cç]ais\b|\bfrancophone\b|\bb2\b|\bc1\b", text, re.IGNORECASE)) and \
             bool(re.search(r"fran[cç]ais|francophone", text, re.IGNORECASE))
    has_en = bool(re.search(r"\benglish\b|\bfluent\b|\bprofessional proficiency\b", text, re.IGNORECASE))

    if has_fr and has_en:
        return "BOTH", True
    if has_fr:
        return "FR", True
    if has_en:
        return "EN", True
    # You said accept unknown
    return "UNKNOWN", True

def main():
    ws = connect_worksheet()

    # Pull all rows as records using header row
    rows = ws.get_all_records()  # list[dict], each dict keyed by header names
    headers = ws.row_values(1)

    required_cols = ["status", "description", "title"]
    for col in required_cols:
        if col not in headers:
            raise RuntimeError(f"Missing column in sheet: '{col}'")

    # Find column indexes for updates
    def col_idx(name: str) -> int:
        return headers.index(name) + 1  # 1-based

    # Ensure optional columns exist
    optional = ["years_required_guess", "junior_ok", "language", "language_ok", "notes"]
    missing = [c for c in optional if c not in headers]
    if missing:
        raise RuntimeError(
            "Add these columns to your sheet first: " + ", ".join(missing)
        )

    updates = []  # list of (row_number, {col_name: value})

    for i, rec in enumerate(rows, start=2):  # data starts at row 2
        status = (rec.get("status") or "").strip().upper()
        if status != "NEW":
            continue

        title = norm_text(str(rec.get("title") or ""))
        desc = norm_text(str(rec.get("description") or ""))
        full = f"{title} {desc}"

        notes = []

        # hard exclusions
        if contains_any(full, NO_INTERNSHIPS):
            updates.append((i, {
                "years_required_guess": "",
                "junior_ok": "FALSE",
                "language": "UNKNOWN",
                "language_ok": "TRUE",
                "notes": "Excluded: internship/alternance/apprenticeship detected",
                "status": "SKIPPED",
            }))
            continue

        if contains_any(full, SENIOR_NEGATIVE):
            notes.append("Senior keyword detected")
            # still check years; but senior keywords are enough to skip
            updates.append((i, {
                "years_required_guess": "",
                "junior_ok": "FALSE",
                "language": detect_language(full)[0],
                "language_ok": "TRUE",
                "notes": "Excluded: senior role indicators",
                "status": "SKIPPED",
            }))
            continue

        # years requirement
        years, evidence = extract_years_required(full)
        if years is None:
            # your rule: assume junior
            junior_ok = True
            years_guess = ""
            notes.append("No explicit years found → assumed junior")
        else:
            years_guess = str(years)
            if years <= 2:
                junior_ok = True
                notes.append(f"Explicit years requirement OK: {evidence}")
            else:
                junior_ok = False
                notes.append(f"Excluded: years requirement too high ({evidence})")

        language, language_ok = detect_language(full)

        if not junior_ok:
            updates.append((i, {
                "years_required_guess": years_guess,
                "junior_ok": "FALSE",
                "language": language,
                "language_ok": "TRUE" if language_ok else "FALSE",
                "notes": "; ".join(notes),
                "status": "SKIPPED",
            }))
            continue

        # optional: add a note if junior signals exist
        if contains_any(full, JUNIOR_POSITIVE):
            notes.append("Junior signal keywords present")

        updates.append((i, {
            "years_required_guess": years_guess,
            "junior_ok": "TRUE",
            "language": language,
            "language_ok": "TRUE" if language_ok else "FALSE",
            "notes": "; ".join(notes),
            "status": "READY_LLM",
        }))

    if not updates:
        print("ℹ️ No NEW rows to process.")
        return

    # Batch update cells for each row
    cell_updates = []
    for row_num, data in updates:
        for k, v in data.items():
            cell_updates.append(gspread.Cell(row_num, col_idx(k), str(v)))

    ws.update_cells(cell_updates, value_input_option="RAW")
    print(f"✅ Updated {len(updates)} rows (NEW → READY_LLM / SKIPPED).")

if __name__ == "__main__":
    main()
