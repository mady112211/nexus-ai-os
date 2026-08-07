import json
from app.database import SessionLocal, Memory


class MemoryManager:
    """Simple memory system for NEXUS AI OS"""

    @staticmethod
    def _serialize(content):
        if isinstance(content, (dict, list)):
            return json.dumps(content)
        return str(content)

    @staticmethod
    def _deserialize(content):
        try:
            return json.loads(content)
        except Exception:
            return content

    @staticmethod
    def save_memory(user_id: int, memory_type: str, content, importance: int = 5):
        db = SessionLocal()
        try:
            memory = Memory(
                user_id=user_id,
                memory_type=memory_type,
                content=MemoryManager._serialize(content),
                importance=importance,
            )
            db.add(memory)
            db.commit()
            db.refresh(memory)
            return memory.id
        finally:
            db.close()

    @staticmethod
    def save_project_memory(user_id: int, mission_id: int, mission_title: str, goal: str, final_report: str):
        content = {
            "mission_id": mission_id,
            "mission_title": mission_title,
            "goal": goal,
            "final_report": final_report[:500],
        }
        return MemoryManager.save_memory(
            user_id=user_id,
            memory_type="project_summary",
            content=content,
            importance=8,
        )

    @staticmethod
    def save_preference(user_id: int, title: str, value: str):
        content = {
            "title": title,
            "value": value,
        }
        return MemoryManager.save_memory(
            user_id=user_id,
            memory_type="user_preference",
            content=content,
            importance=7,
        )

    @staticmethod
    def get_memories(user_id: int, memory_type: str = None, limit: int = 50):
        db = SessionLocal()
        try:
            query = db.query(Memory).filter(Memory.user_id == user_id)
            if memory_type:
                query = query.filter(Memory.memory_type == memory_type)
            memories = query.order_by(Memory.created_at.desc()).limit(limit).all()
            return [
                {
                    "id": m.id,
                    "memory_type": m.memory_type,
                    "content": m.content,
                    "parsed_content": MemoryManager._deserialize(m.content),
                    "importance": m.importance,
                    "created_at": str(m.created_at),
                }
                for m in memories
            ]
        finally:
            db.close()

    @staticmethod
    def get_last_project_context(user_id: int):
        db = SessionLocal()
        try:
            memory = (
                db.query(Memory)
                .filter(
                    Memory.user_id == user_id,
                    Memory.memory_type == "project_summary",
                )
                .order_by(Memory.created_at.desc())
                .first()
            )
            if not memory:
                return None
            return {
                "id": memory.id,
                "memory_type": memory.memory_type,
                "content": memory.content,
                "parsed_content": MemoryManager._deserialize(memory.content),
                "importance": memory.importance,
                "created_at": str(memory.created_at),
            }
        finally:
            db.close()

    @staticmethod
    def search_memories(user_id: int, keyword: str, limit: int = 20):
        db = SessionLocal()
        try:
            memories = (
                db.query(Memory)
                .filter(
                    Memory.user_id == user_id,
                    Memory.content.contains(keyword),
                )
                .order_by(Memory.created_at.desc())
                .limit(limit)
                .all()
            )
            return [
                {
                    "id": m.id,
                    "memory_type": m.memory_type,
                    "content": m.content,
                    "parsed_content": MemoryManager._deserialize(m.content),
                    "importance": m.importance,
                    "created_at": str(m.created_at),
                }
                for m in memories
            ]
        finally:
            db.close()