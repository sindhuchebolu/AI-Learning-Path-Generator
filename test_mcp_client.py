"""
test_mcp_client.py
Comprehensive test suite verifying the AI Learning Path Generator MCP Server.
Tests tool discovery, execution, input validation, resources, and prompt handling
through the official Model Context Protocol (MCP) server interface.
"""

import asyncio
import sys

# Ensure UTF-8 output on Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from mcp_server import mcp


async def run_mcp_tests():
    print("=" * 65)
    print("🚀 STARTING OFFICIAL MODEL CONTEXT PROTOCOL (MCP) VERIFICATION")
    print("=" * 65)

    # 1. Test Tool Discovery (MCP list_tools)
    print("\n🔍 1. Testing MCP Tool Discovery (list_tools)...")
    tools = await mcp.list_tools()
    tool_names = [t.name for t in tools]
    print(f"   Registered MCP Tools count: {len(tools)}")
    for t in tools:
        print(f"   • Tool: '{t.name}' — {t.description[:60]}...")
        
    expected_tools = ["generate_learning_plan", "get_learning_resources", "create_daily_study_schedule"]
    for expected in expected_tools:
        assert expected in tool_names, f"Expected tool '{expected}' missing from MCP server!"
    print("   ✅ Tool discovery test passed!")

    # 2. Test Tool Execution: generate_learning_plan
    print("\n🛠️ 2. Testing MCP Tool Execution: 'generate_learning_plan'...")
    plan_result = await mcp.call_tool(
        "generate_learning_plan",
        {
            "skill": "Model Context Protocol",
            "student_name": "MCP Student",
            "level": "Intermediate",
            "duration_days": 10,
            "daily_hours": 2.0,
            "learning_goal": "Build custom MCP servers for Claude and Antigravity"
        }
    )
    assert not plan_result.is_error, "Tool call returned is_error=True"
    assert len(plan_result.content) > 0, "No content returned from tool"
    output_text = plan_result.content[0].text
    assert "Learning Objectives" in output_text, "Output missing 'Learning Objectives'"
    assert "Weekly Study Plan" in output_text, "Output missing 'Weekly Study Plan'"
    assert "Mini-Project" in output_text or "Capstone" in output_text, "Output missing project section"
    print(f"   ✅ 'generate_learning_plan' executed successfully! (Output length: {len(output_text)} chars)")

    # 3. Test Tool Execution: get_learning_resources
    print("\n📚 3. Testing MCP Tool Execution: 'get_learning_resources'...")
    res_result = await mcp.call_tool(
        "get_learning_resources",
        {"skill": "Python", "level": "Beginner"}
    )
    assert not res_result.is_error
    res_text = res_result.content[0].text
    assert "Curated Learning Resources" in res_text
    print(f"   ✅ 'get_learning_resources' executed successfully! (Output length: {len(res_text)} chars)")

    # 4. Test Tool Execution: create_daily_study_schedule
    print("\n⏰ 4. Testing MCP Tool Execution: 'create_daily_study_schedule'...")
    sched_result = await mcp.call_tool(
        "create_daily_study_schedule",
        {"skill": "Docker & Containers", "duration_days": 5, "daily_hours": 2.0}
    )
    assert not sched_result.is_error
    sched_text = sched_result.content[0].text
    assert "Daily Study Schedule" in sched_text
    assert "Day 01" in sched_text
    print(f"   ✅ 'create_daily_study_schedule' executed successfully! (Output length: {len(sched_text)} chars)")

    # 5. Test Input Validation & Error Handling
    print("\n🛡️ 5. Testing Defensive Input Validation & Error Recovery...")
    err_result = await mcp.call_tool(
        "generate_learning_plan",
        {"skill": ""}
    )
    err_text = err_result.content[0].text
    assert "cannot be empty" in err_text or "Error" in err_text, "Server did not reject empty skill parameter"
    print("   ✅ Empty argument rejected cleanly with descriptive validation message.")

    # 6. Test MCP Resource Discovery & Read
    print("\n📦 6. Testing MCP Resource: 'learning://curriculum-catalog'...")
    resources = await mcp.list_resources()
    resource_uris = [str(r.uri) for r in resources]
    print(f"   Available MCP Resources: {resource_uris}")
    catalog_res = await mcp.read_resource("learning://curriculum-catalog")
    catalog_text = catalog_res[0].content if isinstance(catalog_res, list) else str(catalog_res)
    assert "Supported Learning Curriculum Domains" in catalog_text
    print("   ✅ MCP Resource read successfully!")

    # 7. Test MCP Prompt Discovery & Retrieval
    print("\n💬 7. Testing MCP Prompt: 'study_advisor'...")
    prompts = await mcp.list_prompts()
    prompt_names = [p.name for p in prompts]
    print(f"   Available MCP Prompts: {prompt_names}")
    advisor_prompt = await mcp.get_prompt("study_advisor", {"skill": "Python", "goal": "Automate daily tasks"})
    print(f"   Prompt messages returned: {len(advisor_prompt.messages)}")
    assert len(advisor_prompt.messages) > 0
    print("   ✅ MCP Prompt retrieved successfully!")

    print("\n" + "=" * 65)
    print("🎉 ALL 7 MCP PROTOCOL TESTS COMPLETED AND VERIFIED 100% PASSING!")
    print("=" * 65)


if __name__ == "__main__":
    asyncio.run(run_mcp_tests())
