import os
import shutil

src = r"d:\hospital-api\web\statics\admin"
dst = r"d:\hospital-api\web\static"

if os.path.exists(dst):
    shutil.rmtree(dst)

shutil.copytree(src, dst)
print("Copied web/statics/admin to web/static successfully!")
