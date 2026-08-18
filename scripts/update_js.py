import os
import glob

js_dir = r"web\statics\admin\js"
js_files = glob.glob(os.path.join(js_dir, "*.js"))

for js_file in js_files:
    with open(js_file, 'r', encoding='utf-8') as f:
        content = f.read()
        
    new_content = content.replace("fetch('/web/", "fetch('/api/v1/web/")
    new_content = new_content.replace("fetch('/mobile/", "fetch('/api/v1/mobile/")
    
    if new_content != content:
        with open(js_file, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"Updated {os.path.basename(js_file)}")
    else:
        print(f"No changes in {os.path.basename(js_file)}")
