import os
import shutil

pages_files = [
    "dashboard.html",
    "users.html",
    "admin-staff.html",
    "distributors.html",
    "products.html",
    "orders.html",
    "queries.html",
    "user-detail.html",
    "my-profile.html"
]

partials_dir = r"d:\hospital-api\web\templates\partials"
pages_dir = r"d:\hospital-api\web\templates\pages"

os.makedirs(pages_dir, exist_ok=True)

for fname in pages_files:
    src = os.path.join(partials_dir, fname)
    dst = os.path.join(pages_dir, fname)
    if os.path.exists(src):
        shutil.move(src, dst)
        print(f"Moved {fname} to pages/")

print("Template organization complete.")
