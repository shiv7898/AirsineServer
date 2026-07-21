import os
import shutil

base_path = r"d:\hospital-api\app\api"
web_path = os.path.join(base_path, "web")
mobile_path = os.path.join(base_path, "mobile")

os.makedirs(web_path, exist_ok=True)
os.makedirs(mobile_path, exist_ok=True)

# Function to move or copy
def copy_file(src_name, dest_folder, new_name=None):
    src = os.path.join(base_path, src_name)
    dest_name = new_name if new_name else src_name
    dest = os.path.join(dest_folder, dest_name)
    if os.path.exists(src):
        shutil.copy2(src, dest)
        print(f"Copied {src_name} to {dest_folder}")

def delete_old_file(src_name):
    src = os.path.join(base_path, src_name)
    if os.path.exists(src):
        os.remove(src)
        print(f"Deleted old {src_name}")

# Create __init__.py
with open(os.path.join(web_path, "__init__.py"), "w") as f: f.write("")
with open(os.path.join(mobile_path, "__init__.py"), "w") as f: f.write("")

# Copy auth to both
copy_file("auth_routes.py", web_path, "auth.py")
copy_file("auth_routes.py", mobile_path, "auth.py")
delete_old_file("auth_routes.py")

# Move admin and support to web
copy_file("admin.py", web_path)
copy_file("support.py", web_path)
delete_old_file("admin.py")
delete_old_file("support.py")

# Move patient, doctor, distributor to mobile
copy_file("patient.py", mobile_path)
copy_file("doctor.py", mobile_path)
copy_file("distributor.py", mobile_path)
delete_old_file("patient.py")
delete_old_file("doctor.py")
delete_old_file("distributor.py")

# Copy products and orders to both
copy_file("products.py", web_path)
copy_file("orders.py", web_path)
copy_file("products.py", mobile_path)
copy_file("orders.py", mobile_path)
delete_old_file("products.py")
delete_old_file("orders.py")

# Keep report.py in root or move it? Let's move report to web, as it seems admin related
copy_file("report.py", web_path)
delete_old_file("report.py")

print("Restructure complete")
