"""
upload_to_hf.py
---------------
Uploads code, models, and data files to the Hugging Face Space.
Run from the project root after any local update.

Usage:
    python upload_to_hf.py
"""

from huggingface_hub import HfApi
from pathlib import Path

# ── Configuration ──────────────────────────────────────────────
HF_REPO_ID = "bachirij/energy-intelligence-platform"
REPO_TYPE  = "space"
LOCAL_ROOT = Path(__file__).resolve().parent
# ───────────────────────────────────────────────────────────────

api = HfApi()

# 1. Source code
print("Uploading source code...")
for folder in ["dashboard", "src"]:
    api.upload_folder(
        folder_path=str(LOCAL_ROOT / folder),
        path_in_repo=folder,
        repo_id=HF_REPO_ID,
        repo_type=REPO_TYPE,
    )

# 2. Root files
print("Uploading root files...")
for filename in ["app.py", "requirements.txt", "Dockerfile"]:
    api.upload_file(
        path_or_fileobj=str(LOCAL_ROOT / filename),
        path_in_repo=filename,
        repo_id=HF_REPO_ID,
        repo_type=REPO_TYPE,
    )

# 3. Models
print("Uploading models...")
api.upload_folder(
    folder_path=str(LOCAL_ROOT / "models"),
    path_in_repo="models",
    repo_id=HF_REPO_ID,
    repo_type=REPO_TYPE,
)

# 4. Data - single commit for all data files
print("Uploading data files...")

monitoring_dir = LOCAL_ROOT / "data/monitoring"
latest_report = sorted(monitoring_dir.glob("*.json"))[-1]

import shutil, tempfile

with tempfile.TemporaryDirectory() as tmp:
    tmp = Path(tmp)

    # realtime
    dest_rt = tmp / "data/realtime/country=FR"
    dest_rt.mkdir(parents=True)
    shutil.copy(LOCAL_ROOT / "data/realtime/country=FR/realtime.parquet", dest_rt)

    # featured
    for year in [2024, 2026]:
        src_dir = LOCAL_ROOT / f"data/featured/country=FR/year={year}"
        dest_dir = tmp / f"data/featured/country=FR/year={year}"
        dest_dir.mkdir(parents=True)
        for f in src_dir.glob("*.parquet"):
            shutil.copy(f, dest_dir)

    # monitoring
    dest_mon = tmp / "data/monitoring"
    dest_mon.mkdir(parents=True)
    shutil.copy(latest_report, dest_mon)

    api.upload_folder(
        folder_path=str(tmp),
        path_in_repo="data",
        repo_id=HF_REPO_ID,
        repo_type=REPO_TYPE,
        commit_message="chore: update all data files",
    )