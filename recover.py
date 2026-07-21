import json
import re

path = r"C:\Users\shivsingh\.gemini\antigravity-ide\brain\bf88d482-4c87-4e04-83bc-fd5083f97155\.system_generated\logs\transcript_full.jsonl"
try:
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            d = json.loads(line)
            content = d.get("content", "")
            if "async function viewUser(" in content and "view-user-modal" in content:
                start = content.find("async function viewUser(")
                end = content.find("async function deleteUser", start)
                if end == -1: end = start + 2000
                print(content[start:end])
                break
except Exception as e:
    print(e)
