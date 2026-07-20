import os

def update_file(path, replacements):
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    
    for old, new in replacements:
        content = content.replace(old, new)
        
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Updated {path}")

# 1. Update services/replenishment_workflow.py
workflow_replacements = [
    ("def create_action_from_recommendation(db: Session, rec: ReplenishmentRecommendation) -> ReplenishmentAction:", 
     "def create_action_from_recommendation(db: Session, rec: ReplenishmentRecommendation) -> tuple[ReplenishmentAction, bool]:"),
    ("return existing_action", "return existing_action, False"),
    ("return new_action", "return new_action, True")
]
update_file(r"c:\Projects\Material Availability&Inventory Replenishment Agent\backend\services\replenishment_workflow.py", workflow_replacements)

# 2. Update services/replenishment_orchestration.py
orchestration_replacements = [
    ("action = replenishment_workflow.create_action_from_recommendation(db, rec)",
     "action, was_created = replenishment_workflow.create_action_from_recommendation(db, rec)\n        if not was_created:\n            return action"),
    ("if action.status == \"Drafted\":", "if action.status == \"Drafted\":")
]
update_file(r"c:\Projects\Material Availability&Inventory Replenishment Agent\backend\services\replenishment_orchestration.py", orchestration_replacements)

# 3. Update tests
test_replacements = [
    ("action = replenishment_workflow.create_action_from_recommendation", 
     "action, _ = replenishment_workflow.create_action_from_recommendation"),
    ("action1 = replenishment_workflow.create_action_from_recommendation", 
     "action1, _ = replenishment_workflow.create_action_from_recommendation"),
    ("action2 = replenishment_workflow.create_action_from_recommendation", 
     "action2, _ = replenishment_workflow.create_action_from_recommendation"),
    ("action3 = replenishment_workflow.create_action_from_recommendation", 
     "action3, _ = replenishment_workflow.create_action_from_recommendation"),
    ("action4 = replenishment_workflow.create_action_from_recommendation", 
     "action4, _ = replenishment_workflow.create_action_from_recommendation"),
    ("action5 = replenishment_workflow.create_action_from_recommendation", 
     "action5, _ = replenishment_workflow.create_action_from_recommendation")
]
update_file(r"c:\Projects\Material Availability&Inventory Replenishment Agent\backend\tests\test_execution_service.py", test_replacements)
update_file(r"c:\Projects\Material Availability&Inventory Replenishment Agent\backend\tests\test_replenishment_workflow.py", test_replacements)
