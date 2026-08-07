import json
import re
from ai_core.gateway import call_ai_sync

SYSTEM_PROMPT = """You are NEXUS AI OS Planner. 
Your job is to break down user goals into clear, actionable tasks.

You must respond with ONLY a valid JSON array. No explanation, no markdown, just JSON.

Format:
[
  {
    "task_name": "Task name here",
    "description": "What this task does",
    "assigned_agent": "Research Agent"
  }
]

Available agents:
- Research Agent: web research, market analysis, data collection
- Developer Agent: coding, APIs, technical solutions  
- Content Agent: writing, marketing, social media
"""

def parse_goal(goal: str) -> list:
    """Use AI to break goal into tasks"""
    
    prompt = f"""Break this goal into 4-6 specific tasks:

Goal: {goal}

Remember: respond with ONLY a JSON array, nothing else."""

    try:
        response = call_ai_sync(prompt, SYSTEM_PROMPT)
        
        # Extract JSON from response
        json_match = re.search(r'\[.*\]', response, re.DOTALL)
        if json_match:
            tasks = json.loads(json_match.group())
            if isinstance(tasks, list) and len(tasks) > 0:
                return tasks
    except Exception:
        pass
    
    # Fallback tasks if AI fails
    return _fallback_tasks(goal)

def _fallback_tasks(goal: str) -> list:
    """Default tasks when AI is unavailable"""
    return [
        {
            "task_name": "Goal Analysis",
            "description": f"Analyze and understand the goal: {goal[:80]}",
            "assigned_agent": "Research Agent"
        },
        {
            "task_name": "Research & Data Collection",
            "description": "Gather relevant information and data",
            "assigned_agent": "Research Agent"
        },
        {
            "task_name": "Strategy Development",
            "description": "Create action plan based on research",
            "assigned_agent": "Content Agent"
        },
        {
            "task_name": "Implementation Plan",
            "description": "Define technical implementation steps",
            "assigned_agent": "Developer Agent"
        },
        {
            "task_name": "Final Report",
            "description": "Compile results and recommendations",
            "assigned_agent": "Research Agent"
        }
    ]