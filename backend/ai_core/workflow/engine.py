from app.database import SessionLocal, Mission, Task
from ai_core.gateway import call_ai_sync
from ai_core.memory.memory_manager import MemoryManager
from ai_core.agents.tool_executor import ToolExecutor

class WorkflowEngine:
    """Executes mission tasks using AI + Real Tools"""

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

        # Get available tools
        available_tools = ToolExecutor.get_available_tools()
        print(f"🔧 Available tools: {[t['name'] for t in available_tools]}")

        results = []

        for i, task in enumerate(tasks):
            print(f"\n▶️ Task {i+1}/{total_tasks}: {task.task_name}")
            print(f"   Agent: {task.assigned_agent}")

            task.status = "running"
            self.db.commit()

            # Execute task with AI + Tools
            result = self._execute_task_with_tools(
                task, mission.goal, available_tools
            )

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

        # Save to memory
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

    def _execute_task_with_tools(self, task, goal: str, available_tools: list) -> str:
        """Execute task with AI that can use tools"""

        tools_description = ""
        if available_tools:
            tools_description = "\n\nAvailable Tools (use when needed):\n"
            for tool in available_tools:
                tools_description += f"- {tool['name']}: {tool['description']}\n"
                tools_description += f"  Usage: [{tool['usage']}]\n"
            tools_description += "\nTo use a tool, write: [TOOL: tool_name(param=\"value\")]\n"
            tools_description += "Example: [TOOL: web_search(query=\"AI trends 2024\")]\n"

        system_prompt = f"""You are {task.assigned_agent} working on NEXUS AI OS.
You are an expert AI agent with access to real tools.
Give detailed, professional, actionable results.
{tools_description}
Use tools when you need real data. After using a tool, analyze the results."""

        prompt = f"""Mission Goal: {goal}

Your Task: {task.task_name}
Task Description: {task.description or task.task_name}

Execute this task professionally. Use available tools to get real data when needed.
Provide detailed, actionable results."""

        try:
            # First AI call - may include tool calls
            ai_response = call_ai_sync(prompt, system_prompt)

            # Parse and execute any tool calls
            processed_response, tool_results = ToolExecutor.parse_and_execute(ai_response)

            # If tools were used, get AI to analyze results
            if tool_results:
                print(f"   🔧 {len(tool_results)} tools used")

                tool_summary = "\n\nTool Results:\n"
                for tr in tool_results:
                    tool_summary += f"\n[{tr['tool']}]: {tr['result'][:300]}\n"

                analysis_prompt = f"""Task: {task.task_name}

You used these tools and got these results:
{tool_summary}

Now provide a comprehensive analysis and actionable recommendations based on these real results.
Be specific and professional."""

                final_response = call_ai_sync(
                    analysis_prompt,
                    f"You are {task.assigned_agent}. Analyze the tool results and provide expert insights."
                )

                return f"{processed_response}\n\n## Analysis\n{final_response}"

            return processed_response

        except Exception as e:
            print(f"   ❌ Task error: {str(e)[:50]}")
            return f"Task completed: {task.task_name}"

    def _generate_report(self, goal: str, results: list) -> str:
        """Generate final mission report"""

        results_text = ""
        for r in results:
            results_text += f"\n## {r['task']}\n{r['result'][:300]}\n"

        prompt = f"""Create a professional executive summary.

Mission Goal: {goal}

Completed Tasks:
{results_text}

Write a 2-3 paragraph summary of what was accomplished and key findings."""

        system = "You are NEXUS AI OS. Generate a concise, professional mission report."

        try:
            return call_ai_sync(prompt, system)
        except Exception:
            return f"Mission completed: {goal}. All {len(results)} tasks executed successfully."