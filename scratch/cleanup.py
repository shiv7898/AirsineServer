import os
import shutil

if os.path.exists("app/models.py"):
    os.remove("app/models.py")

if os.path.exists("app/schemas.py"):
    shutil.move("app/schemas.py", "app/schemas/__init__.py")

print("Cleanup complete.")
