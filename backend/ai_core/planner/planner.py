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

Available Specialized Agents:
- Research Agent: web research, market analysis, competitor intelligence
- Developer Agent: coding, APIs, technical solutions, architecture
- Content Agent: writing, copywriting, blog posts, social media
- Designer Agent: UI/UX design, branding, visual concepts, logos
- Marketing Agent: marketing strategy, SEO, campaigns, growth
- Data Analyst Agent: data analysis, insights, reports, metrics
- Strategy Agent: business strategy, planning, decision making
- QA Agent: testing, quality assurance, validation
- Finance Agent: financial planning, budgeting, ROI, pricing
- Support Agent: customer support, docs, FAQs, user guidance

Rules:
1. Assign the MOST APPROPRIATE agent for each task
2. Use different agents for different task types
3. Create 4-7 tasks depending on complexity
4. Be specific with task names
"""

def parse_goal(goal: str) -> list:
    """Use AI to break goal into tasks with specialized agents"""
    
    prompt = f"""Break this goal into 4-7 specific tasks. Assign the best specialized agent to each task.

Goal: {goal}

Remember: respond with ONLY a JSON array, use different specialized agents based on task type."""

    try:
        response = call_ai_sync(prompt, SYSTEM_PROMPT)
        
        json_match = re.search(r'\[.*\]', response, re.DOTALL)
        if json_match:
            tasks = json.loads(json_match.group())
            if isinstance(tasks, list) and len(tasks) > 0:
                return tasks
    except Exception:
        pass
    
    return _fallback_tasks(goal)

def _fallback_tasks(goal: str) -> list:
    """Default tasks when AI is unavailable"""
    return [
        {
            "task_name": "Market Research & Analysis",
            "description": f"Research market and competitors for: {goal[:80]}",
            "assigned_agent": "Research Agent"
        },
        {
            "task_name": "Strategic Planning",
            "description": "Create strategic action plan",
            "assigned_agent": "Strategy Agent"
        },
        {
            "task_name": "Content & Messaging",
            "description": "Develop content strategy and messaging",
            "assigned_agent": "Content Agent"
        },
        {
            "task_name": "Marketing Strategy",
            "description": "Design marketing and growth approach",
            "assigned_agent": "Marketing Agent"
        },
        {
            "task_name": "Executive Summary",
            "description": "Compile final report and recommendations",
            "assigned_agent": "Strategy Agent"
        }
    ]