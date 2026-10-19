"""
mcp_server.py
Official Model Context Protocol (MCP) Server for the AI Learning Path Generator.
Implements the Model Context Protocol (JSON-RPC 2.0 over Stdio) using the official
Python MCP SDK (`mcp.server.mcpserver.MCPServer`).

Exposes 3 core tools:
1. generate_learning_plan
2. get_learning_resources
3. create_daily_study_schedule
"""

import sys
import asyncio
from typing import Optional
from mcp.server.mcpserver import MCPServer
from roadmap_generator import (
    generate_learning_roadmap,
    get_learning_resources_data,
    create_study_schedule_data
)

# Initialize official MCP Server
mcp = MCPServer(
    name="ai-learning-path-generator",
    version="1.0.0",
    instructions=(
        "You are connected to the AI Learning Path Generator MCP Server. "
        "Use these tools to generate structured, personalized technical roadmaps, "
        "curate vetted learning resources, and generate daily study schedules for any skill."
    )
)


@mcp.tool()
def generate_learning_plan(
    skill: str,
    student_name: str = "Learner",
    level: str = "Beginner",
    duration_days: int = 14,
    daily_hours: float = 2.0,
    learning_goal: str = "",
    api_key: str = "",
    model_name: str = "gemini-3.8-flash"
) -> str:
    """
    Generate a comprehensive, personalized learning roadmap for any skill.

    Args:
        skill: The technology or skill to master (e.g., 'Python', 'MCP Servers', 'Docker').
        student_name: The name of the learner (default: 'Learner').
        level: Current experience level ('Beginner', 'Intermediate', or 'Advanced').
        duration_days: Total duration in days (1 to 180).
        daily_hours: Dedicated study hours per day (0.5 to 12.0).
        learning_goal: Primary milestone or objective (e.g. 'Build an MCP tool').
        api_key: Optional Google Gemini API Key. If empty, runs in Smart Demo Mode.
        model_name: Google Gemini model name (default: 'gemini-3.8-flash').

    Returns:
        A rich Markdown roadmap with learning objectives, weekly plan, topics, exercises, and mini-project.
    """
    # Defensive input validation
    clean_skill = (skill or "").strip()
    if not clean_skill:
        return "Error: 'skill' argument cannot be empty. Please specify a subject or technology to learn."

    clean_level = level.strip().capitalize() if level else "Beginner"
    if clean_level not in ["Beginner", "Intermediate", "Advanced"]:
        clean_level = "Beginner"

    safe_days = max(1, min(int(duration_days), 180))
    safe_hours = max(0.5, min(float(daily_hours), 12.0))
    safe_goal = learning_goal.strip() or f"Master {clean_skill} and build real-world projects."

    roadmap_md, is_demo, error_note = generate_learning_roadmap(
        student_name=student_name,
        skill=clean_skill,
        level=clean_level,
        duration_days=safe_days,
        daily_hours=safe_hours,
        learning_goal=safe_goal,
        api_key=api_key or None,
        model_name=model_name
    )

    header = ""
    if is_demo:
        if error_note:
            header = f"> [!WARNING]\n> {error_note}\n\n"
        else:
            header = "> [!NOTE]\n> Generated via Smart Heuristic Mode (Set GEMINI_API_KEY for live AI).\n\n"
    else:
        header = "> [!NOTE]\n> Generated live using Google Gemini AI.\n\n"

    return f"{header}{roadmap_md}"


@mcp.tool()
def get_learning_resources(
    skill: str,
    level: str = "Beginner"
) -> str:
    """
    Retrieve curated, vetted documentation links, tutorials, and platforms for a skill.

    Args:
        skill: The skill or subject (e.g., 'Python', 'MCP', 'Machine Learning').
        level: Current experience level ('Beginner', 'Intermediate', or 'Advanced').

    Returns:
        Structured Markdown list of top resources, repositories, and learning sites.
    """
    clean_skill = (skill or "").strip()
    if not clean_skill:
        return "Error: 'skill' argument cannot be empty."

    clean_level = level.strip().capitalize() if level else "Beginner"
    return get_learning_resources_data(skill=clean_skill, level=clean_level)


@mcp.tool()
def create_daily_study_schedule(
    skill: str,
    duration_days: int = 7,
    daily_hours: float = 2.0
) -> str:
    """
    Create an actionable day-by-day and Pomodoro-blocked study schedule.

    Args:
        skill: The skill to study.
        duration_days: Total days to plan (1 to 60).
        daily_hours: Hours available per day (0.5 to 12.0).

    Returns:
        Day-by-day agenda and daily study breakdown.
    """
    clean_skill = (skill or "").strip()
    if not clean_skill:
        return "Error: 'skill' argument cannot be empty."

    safe_days = max(1, min(int(duration_days), 60))
    safe_hours = max(0.5, min(float(daily_hours), 12.0))
    return create_study_schedule_data(skill=clean_skill, duration_days=safe_days, daily_hours=safe_hours)


@mcp.resource("learning://curriculum-catalog")
def curriculum_catalog() -> str:
    """
    Exposes an MCP Resource detailing supported domains and default curriculum tracks.
    """
    return """# Supported Learning Curriculum Domains
- Python Programming & Automation
- Model Context Protocol (MCP) Server Development
- Machine Learning & Data Science
- Full-Stack Web Development (React / Node.js)
- Prompt Engineering & Generative AI Systems
- Cloud Architecture & DevOps (Docker, Kubernetes)
- General Software Engineering
"""


@mcp.prompt("study_advisor")
def study_advisor_prompt(skill: str, goal: str) -> str:
    """
    Exposes an MCP Prompt template for AI models to act as a personalized study advisor.
    """
    return (
        f"You are a mentor guiding a student learning {skill}. "
        f"Their primary goal is: {goal}. "
        "Review their recent progress, provide encouragement, and recommend their next 3 actionable milestones."
    )


def main():
    """
    Runs the MCP server over standard input/output (stdio transport).
    Compatible with Claude Desktop, Antigravity, and any standard MCP host.
    """
    # Suppress verbose debug logs to ensure stdio JSON-RPC remains clean
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
