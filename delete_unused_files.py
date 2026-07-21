import os

files_to_delete = [
    "temp.js",
    "test_syntax.js",
    "package.json",
    "package-lock.json",
    "hospital.db",
    "database.db",
    "seed_db.py",
    "test_admin_products.py",
    "check_data.py",
    "check_db.py",
    "check_nulls.py",
    "print_orders.py",
    "add_column.py",
    "add_columns.py",
    "add_user_columns.py",
    "migrate_queries.py",
    "update_db.py",
    "update_db_pdf.py"
]

print("Starting deletion of unused files...")

for file in files_to_delete:
    if os.path.exists(file):
        try:
            os.remove(file)
            print(f"Successfully deleted: {file}")
        except Exception as e:
            print(f"Error deleting {file}: {e}")
    else:
        print(f"File not found (already deleted): {file}")

print("Clean up finished!")
