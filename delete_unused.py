import os
try:
    os.remove(r"d:\hospital-api\web\templates\partials\user-detail.html")
    print("Deleted user-detail.html")
except Exception as e:
    print(e)
