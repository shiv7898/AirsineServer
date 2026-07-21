import os
import re

api_dir = "app/api"
files = [f for f in os.listdir(api_dir) if f.endswith(".py") and f != "router.py" and f != "__init__.py"]

replacements = [
    (r"import models\b", r"import app.models as models"),
    (r"from models import", r"from app.models import"),
    (r"import schemas\b", r"import app.schemas as schemas"),
    (r"from schemas import", r"from app.schemas import"),
    (r"from utils import", r"from helpers.utils import"),
    (r"from exception import", r"from app.core.exception import"),
    (r"from auth import", r"from app.core.auth import"),
    (r"from config import", r"from app.core.config import"),
    (r"from validators import", r"from helpers.validators import")
]

for file in files:
    path = os.path.join(api_dir, file)
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    
    for old, new in replacements:
        content = re.sub(old, new, content)
    
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

print("Updated imports in app/api")
