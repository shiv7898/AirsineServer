import re

file_path = r"d:\hospital-api\web\statics\admin\js\app.js"
with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

# Replace specific API calls with /web prefix
replacements = [
    (r"fetch\('/auth/login'", r"fetch('/web/user/login'"),
    (r"fetch\('/admin/", r"fetch('/web/admin/"),
    (r"fetch\(`/admin/", r"fetch(`/web/admin/"),
    (r"fetch\('/products/", r"fetch('/web/products/"),
    (r"fetch\(`/products/", r"fetch(`/web/products/"),
    (r"fetch\('/support/admin", r"fetch('/web/support/admin"),
    (r"fetch\(`/support/admin", r"fetch(`/web/support/admin"),
]

for old, new in replacements:
    content = re.sub(old, new, content)

with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)

print("Updated app.js")
