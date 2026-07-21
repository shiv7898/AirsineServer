import os

files_to_delete = [
    r"d:\hospital-api\restructure.py",
    r"d:\hospital-api\update_app_js.py"
]

for f in files_to_delete:
    if os.path.exists(f):
        os.remove(f)
