import os
import shutil

# Step 1: Create directories
dirs = [
    "app/models", "app/schemas", "app/services", "app/core", "app/api", 
    "web/templates", "web/statics", "helpers"
]
for d in dirs:
    os.makedirs(d, exist_ok=True)

# Step 2: Move files
moves = [
    ("utils.py", "helpers/utils.py"),
    ("validators.py", "helpers/validators.py"),
    ("config.py", "app/core/config.py"),
    ("exception.py", "app/core/exception.py"),
    ("auth.py", "app/core/auth.py")
]

for src, dst in moves:
    if os.path.exists(src):
        shutil.move(src, dst)

if os.path.exists("routers"):
    for item in os.listdir("routers"):
        shutil.move(os.path.join("routers", item), "app/api/")
    os.rmdir("routers")

if os.path.exists("static"):
    for item in os.listdir("static"):
        shutil.move(os.path.join("static", item), "web/statics/")
    os.rmdir("static")

# Step 3: We need to split models.py and schemas.py. 
# We'll do this in a subsequent step, for now, just move them to the app directory so they aren't lost if the script is re-run.
if os.path.exists("models.py"):
    shutil.move("models.py", "app/models.py")

if os.path.exists("schemas.py"):
    shutil.move("schemas.py", "app/schemas.py")

print("Files moved successfully. Now we need to update imports.")
