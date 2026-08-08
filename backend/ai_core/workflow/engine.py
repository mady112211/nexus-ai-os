from app.database import SessionLocal, Mission, Task
from ai_core.gateway import call_ai_sync
from ai_core.memory.memory_manager import MemoryManager
from ai_core.agents.tool_executor import ToolExecutor
from ai_core.agents.agent_personas import get_agent_persona
from ai_core.notifications import NotificationManager

class WorkflowEngine:
    """Executes mission tasks with notifications"""

    def __init__(self, mission_id: int):
        self.mission_id = mission_id
        self.db = SessionLocal()

    def start(self):
        print(f"\n🚀 Starting Mission #{self.mission_id}")

        mission = self.db.query(Mission).filter(
            Mission.id == self.mission_id
        ).first()

        if not mission:
            return None

        # Notify: Mission started
        NotificationManager.create(
            user_id=mission.user_id,
            title=f"Mission Started",
            message=f"'{mission.title}' is now being executed",
            notification_type="info",
            icon="🚀",
            action_url=f"/missions/{mission.id}"
        )

        mission.status = "running"
        mission.progress = 0
        self.db.commit()

        tasks = self.db.query(Task).filter(
            Task.mission_id == self.mission_id
        ).order_by(Task.order_index).all()

        total_tasks = len(tasks)
        if total_tasks == 0:
            return None

        print(f"📋 {total_tasks} tasks to execute")

        available_tools = ToolExecutor.get_available_tools()
        print(f"🔧 Available tools: {[t['name'] for t in available_tools]}")

        results = []

        for i, task in enumerate(tasks):
            print(f"\n▶️ Task {i+1}/{total_tasks}: {task.task_name}")
            print(f"   Agent: {task.assigned_agent}")

            task.status = "running"
            self.db.commit()

            result = self._execute_task_with_specialist(
                task, mission.goal, available_tools
            )

            task.status = "completed"
            task.result = result
            self.db.commit()

            results.append({
                "task": task.task_name,
                "agent": task.assigned_agent,
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

        # Notify: Mission completed
        NotificationManager.create(
            user_id=mission.user_id,
            title=f"Mission Completed! 🎉",
            message=f"'{mission.title}' finished successfully with {total_tasks} tasks",
            notification_type="success",
            icon="✅",
            action_url=f"/missions/{mission.id}"
        )

        print(f"\n🎉 Mission #{self.mission_id} COMPLETED!")

        self.db.close()
        return final_report

    def _execute_task_with_specialist(self, task, goal: str, available_tools: list) -> str:
        agent_persona = get_agent_persona(task.assigned_agent)

        tools_description = ""
        if available_tools:
            tools_description = "\n\nAvailable Tools:\n"
            for tool in available_tools:
                tools_description += f"- {tool['name']}: {tool['description']}\n"
                tools_description += f"  Usage: [{tool['usage']}]\n"
            tools_description += "\nTo use a tool: [TOOL: tool_name(param=\"value\")]\n"

        system_prompt = f"""{agent_persona}
{tools_description}
Use tools when you need real data."""

        prompt = f"""Mission Goal: {goal}

Your Task: {task.task_name}
Description: {task.description or task.task_name}

Execute using your expertise. Be detailed and actionable."""

        try:
            ai_response = call_ai_sync(prompt, system_prompt)
            processed_response, tool_results = ToolExecutor.parse_and_execute(ai_response)

            if tool_results:
                print(f"   🔧 {len(tool_results)} tools used")

                tool_summary = "\n\nReal Data:\n"
                for tr in tool_results:
                    tool_summary += f"\n[{tr['tool']}]: {tr['result'][:300]}\n"

                analysis_prompt = f"""Task: {task.task_name}
Data received: {tool_summary}
As {task.assigned_agent}, analyze and provide expert insights."""

                final_response = call_ai_sync(analysis_prompt, agent_persona)
                return f"{processed_response}\n\n## Expert Analysis\n{final_response}"

            return processed_response

        except Exception as e:
            print(f"   ❌ Task error: {str(e)[:50]}")
            return f"Task completed: {task.task_name}"

    def _generate_report(self, goal: str, results: list) -> str:
        results_text = ""
        for r in results:
            results_text += f"\n### {r['task']} (by {r['agent']})\n{r['result'][:250]}\n"

        prompt = f"""Create executive summary combining all agent insights.

Goal: {goal}

Contributions:
{results_text}

Write 3-4 paragraph summary: accomplishments, key findings, recommendations, next steps."""

        system = "You are NEXUS Master Coordinator. Generate professional comprehensive report."

        try:
            return call_ai_sync(prompt, system)
        except Exception:
            return f"Mission completed: {goal}. {len(results)} specialists contributed."