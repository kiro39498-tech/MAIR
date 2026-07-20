import os

replacements = [
    ("connectors/execution_connector.py", "datetime.utcnow()", "datetime.now(timezone.utc)"),
    ("persistence/models.py", "datetime.utcnow", "lambda: datetime.now(timezone.utc)"),
    ("persistence/repository.py", "datetime.utcnow()", "datetime.now(timezone.utc)"),
    ("services/replenishment_workflow.py", "datetime.utcnow()", "datetime.now(timezone.utc)"),
    ("tests/test_notification_service.py", "datetime.utcnow()", "datetime.now(timezone.utc)"),
    ("tests/test_persistence.py", "datetime.utcnow()", "datetime.now(timezone.utc)"),
]

for filepath, old, new in replacements:
    path = os.path.join(r"c:\Projects\Material Availability&Inventory Replenishment Agent\backend", filepath)
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
            
        if "from datetime import timezone" not in content and old in content:
            # add import at the top
            content = "from datetime import timezone\n" + content
            
        content = content.replace(old, new)
        
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Updated {filepath}")
