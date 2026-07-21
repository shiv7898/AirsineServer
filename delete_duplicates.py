import os

files = [
    r"d:\hospital-api\app\api\mobile\products.py",
    r"d:\hospital-api\app\api\mobile\orders.py"
]

for f in files:
    if os.path.exists(f):
        os.remove(f)
        print(f"Deleted {f}")
    else:
        print(f"File not found: {f}")
