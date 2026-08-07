from ai_core.planner.planner import parse_goal

def create_tasks_for_mission(goal: str) -> list:
    """Create tasks for a mission using AI planner"""
    tasks = parse_goal(goal)
    
    # Add order index
    for i, task in enumerate(tasks):
        task["order_index"] = i
        
    return tasks