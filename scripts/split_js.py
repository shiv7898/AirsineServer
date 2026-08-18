import re
import os
import shutil

app_js_path = r'd:\hospital-api\web\statics\admin\js\app.js'
out_dir = r'd:\hospital-api\web\statics\admin\js'

# Create a backup
shutil.copyfile(app_js_path, app_js_path + '.backup')

with open(app_js_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

sections = []
current_section_name = "1: GLOBALS & UTILITIES"
current_lines = []

for line in lines:
    match = re.search(r'// SECTION (\d+): (.*)', line)
    if match:
        sections.append((current_section_name, current_lines))
        current_section_name = f"{match.group(1)}: {match.group(2).strip()}"
        current_lines = [line]
    else:
        current_lines.append(line)

if current_lines:
    sections.append((current_section_name, current_lines))

file_mapping = {
    'auth.js': ['4: AUTHENTICATION & LOGIN'],
    'users.js': [
        '6: USERS',
        '7: ADMIN',
        '8: DISTRIBUTORS',
        '9: FETCHING',
        '10: USER'
    ],
    'products.js': [
        '11: PRODUCTS',
        '12: PRODUCTS'
    ],
    'orders.js': [
        '12: ORDERS MANAGEMENT',
        '13: ORDERS MANAGEMENT',
        '14: ORDERS MANAGEMENT'
    ],
    'queries.js': [
        '15: QUERIES MANAGEMENT',
        '14: QUERIES'
    ]
}

# For app.js, we keep the core sections
app_js_sections = [
    '1: GLOBALS & UTILITIES',
    '2: INITIALIZATION & ROUTING',
    '3: ROLE-BASED ACCESS CONTROL (RBAC) & PERMISSIONS',
    '5: DASHBOARD & CHARTS'
]

# Write out the mapped files
for filename, target_sections in file_mapping.items():
    content = ""
    for name, lines_list in sections:
        if any(ts in name for ts in target_sections) or any(name.startswith(ts.split(':')[0] + ':') for ts in target_sections):
            content += "".join(lines_list) + "\n"
    
    if content.strip():
        with open(os.path.join(out_dir, filename), 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Created {filename} with mapped sections.")

# Overwrite app.js with only core sections
core_content = ""
for name, lines_list in sections:
    # Keep if it matches app_js_sections, or if it doesn't match ANY of the extracted files
    is_extracted = False
    for target_sections in file_mapping.values():
        if any(ts in name for ts in target_sections) or any(name.startswith(ts.split(':')[0] + ':') for ts in target_sections):
            is_extracted = True
            break
            
    if not is_extracted:
        core_content += "".join(lines_list) + "\n"

with open(app_js_path, 'w', encoding='utf-8') as f:
    f.write(core_content)

print("Updated app.js with core sections only.")
