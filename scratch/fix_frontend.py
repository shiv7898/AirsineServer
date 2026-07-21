import os
import re

html_file = "web/statics/admin/index.html"

with open(html_file, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Extract CSS
os.makedirs("web/statics/admin/css", exist_ok=True)
styles = re.findall(r"<style>(.*?)</style>", content, re.DOTALL)
if styles:
    with open("web/statics/admin/css/style.css", "w", encoding="utf-8") as f:
        f.write(styles[0].strip())
    content = re.sub(r"<style>.*?</style>", '<link rel="stylesheet" href="/admin-ui/css/style.css">', content, flags=re.DOTALL)

# 2. Extract JS
os.makedirs("web/statics/admin/js", exist_ok=True)
scripts = re.findall(r"<script>(.*?)</script>", content, re.DOTALL)
if scripts:
    for s in scripts:
        if "API_BASE_URL" in s or "switchTab" in s:
            with open("web/statics/admin/js/app.js", "w", encoding="utf-8") as f:
                f.write(s.strip())
            content = content.replace(f"<script>{s}</script>", '<script src="/admin-ui/js/app.js"></script>')
            break

# 3. Extract sections safely
os.makedirs("web/templates/partials", exist_ok=True)

view_pattern = re.compile(r'<div\s+id="([^"]+-view)"\s+class="panel-page[^>]*>')

def extract_view(content, match):
    start_idx = match.start()
    id_name = match.group(1)
    
    div_count = 0
    in_view = False
    i = start_idx
    while i < len(content):
        # Match <div with a space or >
        if content[i:i+4] == "<div" and content[i+4] in " >\n\r\t":
            div_count += 1
            in_view = True
            i += 4
            continue
        elif content[i:i+6] == "</div>":
            div_count -= 1
            if in_view and div_count == 0:
                # Include the full </div> tag
                return id_name, start_idx, i + 6
            i += 6
            continue
        
        i += 1

    return id_name, start_idx, len(content)

views_extracted = []
current_search_idx = 0
while True:
    match = view_pattern.search(content, current_search_idx)
    if not match:
        break
    
    id_name, start, end = extract_view(content, match)
    view_html = content[start:end]
    
    filename = id_name.replace("-view", "") + ".html"
    with open(f"web/templates/partials/{filename}", "w", encoding="utf-8") as f:
        f.write(view_html)
    
    views_extracted.append((id_name, filename, start, end))
    current_search_idx = end

# Replace from bottom to top
views_extracted.sort(key=lambda x: x[2], reverse=True)
for id_name, filename, start, end in views_extracted:
    include_str = "{% include 'partials/" + filename + "' %}"
    content = content[:start] + include_str + content[end:]

with open("web/templates/base.html", "w", encoding="utf-8") as f:
    f.write(content)

print("Frontend properly extracted with correct closing tags!")
