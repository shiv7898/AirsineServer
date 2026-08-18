import os
import shutil

target = r"d:\hospital-api\app\api\mobile"

if os.path.exists(target):
    shutil.rmtree(target)
    print(f"Successfully deleted legacy directory: {target}")
else:
    print("Directory does not exist or already removed.")
