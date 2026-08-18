"""
Run this once to delete all unused one-off/debug/utility scripts from the project root.
Usage:  python scripts\cleanup_unused.py
"""
import os, shutil

BASE = r"d:\hospital-api"

# ── Root-level files that are never imported by the app ──────────────────────
ROOT_FILES = [
    "check_db.py",           # sqlite3 debug dump — project is PostgreSQL now
    "clean_scripts.py",      # meta-script to delete other scripts
    "cleanup.py",            # meta-script to delete other scripts
    "create_superadmin.py",  # one-time bootstrap script, done
    "delete_duplicates.py",  # one-time script
    "delete_models_schemas.py",  # one-time script
    "delete_unused.py",      # one-time script
    "delete_unused_files.py",    # one-time script
    "recover.py",            # reads IDE transcript logs — not app code
    "restructure.py",        # one-time folder restructuring script
    "test_edit.py",          # hardcoded test with expired token
    "update_app_js.py",      # one-time migration script for app.js
    "error_log.txt",         # transient log file
]

# ── Directories that are empty or contain only dev/scratch files ─────────────
DIRS_TO_REMOVE = [
    r"app\services",     # empty directory
    "scratch",           # scratch/dev files, not part of the app
]

deleted, skipped = [], []

for fname in ROOT_FILES:
    path = os.path.join(BASE, fname)
    if os.path.exists(path):
        os.remove(path)
        deleted.append(fname)
    else:
        skipped.append(fname)

for dname in DIRS_TO_REMOVE:
    path = os.path.join(BASE, dname)
    if os.path.exists(path):
        shutil.rmtree(path)
        deleted.append(dname + "/")
    else:
        skipped.append(dname + "/")

print(f"\n✅ Deleted ({len(deleted)}):")
for d in deleted:
    print(f"   {d}")

if skipped:
    print(f"\n⚠️  Already gone ({len(skipped)}):")
    for s in skipped:
        print(f"   {s}")

print("\nDone. Run: uvicorn main:app --reload  to confirm the app still starts.")
