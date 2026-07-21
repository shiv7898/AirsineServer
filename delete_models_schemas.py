import os

files_to_delete = [
    r"d:\hospital-api\app\models.py",
    r"d:\hospital-api\app\schemas.py"
]

for f in files_to_delete:
    try:
        if os.path.exists(f):
            os.remove(f)
            print(f"Deleted {f}")
    except Exception as e:
        print(e)
