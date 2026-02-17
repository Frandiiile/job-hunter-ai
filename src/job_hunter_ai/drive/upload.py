from __future__ import annotations

import os
from pathlib import Path
from typing import Optional

from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload


DRIVE_SCOPES = ["https://www.googleapis.com/auth/drive"]


def _get_drive_service():
    creds_path = os.getenv("GOOGLE_CREDENTIALS_PATH")
    if not creds_path:
        raise RuntimeError(
            "GOOGLE_CREDENTIALS_PATH is not set. Point it to your service account JSON."
        )

    creds_file = Path(creds_path)
    if not creds_file.exists():
        raise RuntimeError(f"Service account JSON not found: {creds_file}")

    creds = Credentials.from_service_account_file(str(creds_file), scopes=DRIVE_SCOPES)
    return build("drive", "v3", credentials=creds, cache_discovery=False)


def _guess_target_folder_id(file_path: Path) -> Optional[str]:
    name = file_path.name.lower()
    # Simple heuristic; adjust if your filenames differ
    if "cover" in name:
        return os.getenv("GOOGLE_DRIVE_COVER_LETTERS_FOLDER_ID")
    if "cv" in name or "resume" in name:
        return os.getenv("GOOGLE_DRIVE_RESUMES_FOLDER_ID")
    return os.getenv("GOOGLE_DRIVE_FOLDER_ID")  # optional fallback


def upload_to_drive(file_path: Path | str, folder_id: str | None = None) -> str:
    """
    Uploads a file to Google Drive (service account).
    Returns a webViewLink.
    """
    file_path = Path(file_path)
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    service = _get_drive_service()

    target_folder_id = folder_id or _guess_target_folder_id(file_path)
    if not target_folder_id:
        raise RuntimeError(
            "No Drive folder configured. Set GOOGLE_DRIVE_RESUMES_FOLDER_ID and "
            "GOOGLE_DRIVE_COVER_LETTERS_FOLDER_ID (or pass folder_id explicitly)."
        )

    file_metadata = {"name": file_path.name, "parents": [target_folder_id]}

    media = MediaFileUpload(
        str(file_path),
        resumable=True,
    )

    created = (
        service.files()
        .create(body=file_metadata, media_body=media, fields="id, webViewLink")
        .execute()
    )

    return created["webViewLink"]
