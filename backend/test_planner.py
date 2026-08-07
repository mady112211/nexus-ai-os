import sys
sys.path.insert(0, '.')

print("Testing AI Planner...")

from ai_core.planner.planner import parse_goal

goal = "Build a mobile app for food delivery startup"
print(f"Goal: {goal}")
print("Calling AI...")

tasks = parse_goal(goal)
print(f"\nTasks received: {len(tasks)}")
for t in tasks:
    print(f"- {t['task_name']} | {t['assigned_agent']}")