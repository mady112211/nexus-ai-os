from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import os

# Database setup
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///nexus.db")
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# ============ MODELS ============

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(50), default="user")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    missions = relationship("Mission", back_populates="user")
    memories = relationship("Memory", back_populates="user")

class Mission(Base):
    __tablename__ = "missions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    title = Column(String(255), nullable=False)
    goal = Column(Text, nullable=False)
    status = Column(String(50), default="pending")
    progress = Column(Integer, default=0)
    result = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="missions")
    tasks = relationship("Task", back_populates="mission")

class Task(Base):
    __tablename__ = "tasks"
    
    id = Column(Integer, primary_key=True, index=True)
    mission_id = Column(Integer, ForeignKey("missions.id"))
    task_name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    assigned_agent = Column(String(100), nullable=True)
    status = Column(String(50), default="pending")
    result = Column(Text, nullable=True)
    order_index = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    mission = relationship("Mission", back_populates="tasks")

class Memory(Base):
    __tablename__ = "memories"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    memory_type = Column(String(50), nullable=False)
    content = Column(Text, nullable=False)
    importance = Column(Integer, default=5)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="memories")

class Agent(Base):
    __tablename__ = "agents"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    role = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

# ============ DB FUNCTIONS ============

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    Base.metadata.create_all(bind=engine)
    
    # Default agents
    db = SessionLocal()
    try:
        if db.query(Agent).count() == 0:
            agents = [
                Agent(name="Nova Research", role="Research Agent", 
                      description="Market research and data analysis"),
                Agent(name="Nova Developer", role="Developer Agent",
                      description="Coding and technical solutions"),
                Agent(name="Nova Content", role="Content Agent",
                      description="Content creation and marketing"),
            ]
            db.add_all(agents)
            db.commit()
            print("✅ Default agents created!")
    finally:
        db.close()