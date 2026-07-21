import os
import shutil

old_dir = r"d:\hospital-api\app\api\web"

if os.path.exists(old_dir):
    try:
        shutil.rmtree(old_dir)
        print(f"Successfully deleted old directory: {old_dir}")
    except Exception as e:
        print(f"Error deleting directory: {e}")
else:
    print(f"Directory does not exist: {old_dir}")
