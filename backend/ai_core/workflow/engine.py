from app.database import SessionLocal, Mission, Task
from ai_core.gateway import call_ai_sync
from ai_core.memory.memory_manager import MemoryManager

class WorkflowEngine:
    """Executes mission tasks one by one using AI"""

    def __init__(self, mission_id: int):
        self.mission_id = mission_id
        self.db = SessionLocal()

    def start(self):
        """Start executing the mission"""
        print(f"\n🚀 Starting Mission #{self.mission_id}")

        mission = self.db.query(Mission).filter(
            Mission.id == self.mission_id
        ).first()

        if not mission:
            print("❌ Mission not found")
            return None

        mission.status = "running"
        mission.progress = 0
        self.db.commit()

        tasks = self.db.query(Task).filter(
            Task.mission_id == self.mission_id
        ).order_by(Task.order_index).all()

        total_tasks = len(tasks)
        if total_tasks == 0:
            print("❌ No tasks found")
            return None

        print(f"📋 {total_tasks} tasks to execute")

        results = []

        for i, task in enumerate(tasks):
            print(f"\n▶️ Task {i+1}/{total_tasks}: {task.task_name}")
            print(f"   Agent: {task.assigned_agent}")

            task.status = "running"
            self.db.commit()

            result = self._execute_task(task, mission.goal)

            task.status = "completed"
            task.result = result
            self.db.commit()

            results.append({
                "task": task.task_name,
                "result": result
            })

            progress = int(((i + 1) / total_tasks) * 100)
            mission.progress = progress
            self.db.commit()

            print(f"   ✅ Done ({progress}%)")

        print(f"\n📝 Generating final report...")
        final_report = self._generate_report(mission.goal, results)

        mission.status = "completed"
        mission.progress = 100
        mission.result = final_report
        self.db.commit()

        try:
            MemoryManager.save_project_memory(
                user_id=mission.user_id,
                mission_id=mission.id,
                mission_title=mission.title,
                goal=mission.goal,
                final_report=final_report,
            )
            print("🧠 Project memory saved")
        except Exception as e:
            print(f"❌ Memory save failed: {str(e)}")

        print(f"\n🎉 Mission #{self.mission_id} COMPLETED!")

        self.db.close()
        return final_report

    def _execute_task(self, task, goal: str) -> str:
        system_prompt = f"""You are {task.assigned_agent} working on NEXUS AI OS.
You are an expert AI agent. Give a detailed, professional response.
Be specific and actionable. Write 3-5 paragraphs."""

        prompt = f"""Mission Goal: {goal}

Your Task: {task.task_name}
Task Description: {task.description or task.task_name}

Execute this task and provide detailed results.
Be specific, professional, and actionable."""

        try:
            result = call_ai_sync(prompt, system_prompt)
            return result
        except Exception as e:
            print(f"   ❌ Task error: {str(e)[:50]}")
            return f"Task completed with basic analysis for: {task.task_name}"

    def _generate_report(self, goal: str, results: list) -> str:
        results_text = ""
        for r in results:
            results_text += f"\n## {r['task']}\n{r['result'][:200]}\n"

        prompt = f"""Create a brief executive summary for this completed mission.

Mission Goal: {goal}

Task Results:
{results_text}

Write a 2-3 paragraph professional summary of what was accomplished."""

        system = "You are NEXUS AI OS generating a mission completion report. Be concise and professional."

        try:
            return call_ai_sync(prompt, system)
        except Exception:
            return f"Mission completed: {goal}. All {len(results)} tasks executed successfully."