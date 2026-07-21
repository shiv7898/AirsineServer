import os

src_dir = r"d:\hospital-api\app\api\web"
dst_dir = r"d:\hospital-api\web"

files_to_move = ["admin.py", "auth.py", "orders.py", "products.py", "report.py", "support.py"]

for filename in files_to_move:
    src_path = os.path.join(src_dir, filename)
    dst_path = os.path.join(dst_dir, filename)
    
    with open(src_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Update internal imports
    updated_content = content.replace("from app.api.web.admin import", "from web.admin import")
    updated_content = updated_content.replace("app.api.web.admin", "web.admin")
    
    with open(dst_path, "w", encoding="utf-8") as f:
        f.write(updated_content)
        
    print(f"Copied {filename} to {dst_path} and updated imports")
