import asyncio
from mcp_server.server import mcp
import persistence.models
from persistence.db import Base, engine

Base.metadata.create_all(bind=engine)

async def run():
    tools = await mcp.list_tools()
    print("Tools:")
    for t in tools:
        print(f" - {t.name}")
        
    print("\n--- Calling create_replenishment_action ---")
    res = await mcp.call_tool("create_replenishment_action", {"material_id": "MAT-00124", "plant_id": "PLT-DE-02"})
    print("Result:")
    for content in res:
        print(content.text)
        
    action_id = None
    import json
    for content in res:
        if content.type == "text":
            try:
                data = json.loads(content.text)
                action_id = data.get("action_id")
            except:
                pass
                
    if action_id:
        print(f"\n--- Calling get_replenishment_action_status for {action_id} ---")
        res2 = await mcp.call_tool("get_replenishment_action_status", {"action_id": action_id})
        for content in res2:
            print(content.text)
            
    print("\n--- Calling list_pending_replenishment_actions ---")
    res3 = await mcp.call_tool("list_pending_replenishment_actions", {})
    for content in res3:
        print(content.text)

if __name__ == "__main__":
    asyncio.run(run())
