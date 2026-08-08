from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime, Text, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///nexus.db")
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


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


class Plugin(Base):
    __tablename__ = "plugins"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True)
    slug = Column(String(100), nullable=False, unique=True)
    description = Column(Text, nullable=True)
    version = Column(String(20), default="1.0.0")
    category = Column(String(50), default="general")
    icon = Column(String(10), default="🔌")
    is_enabled = Column(Boolean, default=False)
    is_installed = Column(Boolean, default=True)
    config = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        # ============ 10 SPECIALIZED AGENTS ============
        if db.query(Agent).count() == 0:
            agents = [
                Agent(
                    name="Nova Research",
                    role="Research Agent",
                    description="Market research, data analysis, and competitor intelligence"
                ),
                Agent(
                    name="Nova Developer",
                    role="Developer Agent",
                    description="Coding, APIs, technical architecture, and debugging"
                ),
                Agent(
                    name="Nova Content",
                    role="Content Agent",
                    description="Content creation, copywriting, and social media strategy"
                ),
                Agent(
                    name="Nova Designer",
                    role="Designer Agent",
                    description="UI/UX design, branding, and visual concepts"
                ),
                Agent(
                    name="Nova Marketing",
                    role="Marketing Agent",
                    description="Marketing campaigns, SEO, and growth strategies"
                ),
                Agent(
                    name="Nova Analyst",
                    role="Data Analyst Agent",
                    description="Data analysis, insights, and business intelligence"
                ),
                Agent(
                    name="Nova Strategist",
                    role="Strategy Agent",
                    description="Business strategy, planning, and decision making"
                ),
                Agent(
                    name="Nova QA",
                    role="QA Agent",
                    description="Quality assurance, testing, and validation"
                ),
                Agent(
                    name="Nova Finance",
                    role="Finance Agent",
                    description="Financial planning, budgeting, and ROI analysis"
                ),
                Agent(
                    name="Nova Support",
                    role="Support Agent",
                    description="Customer support, documentation, and user guidance"
                ),
            ]
            db.add_all(agents)
            db.commit()
            print("✅ 10 Specialized agents created!")

        # ============ DEFAULT PLUGINS ============
        if db.query(Plugin).count() == 0:
            plugins = [
                Plugin(
                    name="Web Search",
                    slug="web_search",
                    description="Search the internet for real-time information",
                    category="research",
                    icon="🔍",
                    is_enabled=True,
                    config={"max_results": 5}
                ),
                Plugin(
                    name="File Manager",
                    slug="file_manager",
                    description="Read and write files on your system",
                    category="productivity",
                    icon="📁",
                    is_enabled=True,
                    config={}
                ),
                Plugin(
                    name="Weather",
                    slug="weather",
                    description="Get real-time weather data for any city",
                    category="research",
                    icon="🌤️",
                    is_enabled=True,
                    config={"default_city": "Karachi"}
                ),
                Plugin(
                    name="GitHub",
                    slug="github",
                    description="Connect with GitHub repositories",
                    category="development",
                    icon="🐙",
                    is_enabled=False,
                    config={"token": ""}
                ),
                Plugin(
                    name="Gmail",
                    slug="gmail",
                    description="Send and read emails via Gmail",
                    category="communication",
                    icon="📧",
                    is_enabled=False,
                    config={"email": ""}
                ),
                Plugin(
                    name="Google Docs",
                    slug="google_docs",
                    description="Create and edit Google Documents",
                    category="productivity",
                    icon="📄",
                    is_enabled=False,
                    config={}
                ),
                Plugin(
                    name="Slack",
                    slug="slack",
                    description="Send messages to Slack channels",
                    category="communication",
                    icon="💬",
                    is_enabled=False,
                    config={"webhook_url": ""}
                ),
                Plugin(
                    name="Notion",
                    slug="notion",
                    description="Create and update Notion pages",
                    category="productivity",
                    icon="📓",
                    is_enabled=False,
                    config={"api_key": ""}
                ),
                Plugin(
                    name="WhatsApp",
                    slug="whatsapp",
                    description="Send WhatsApp messages",
                    category="communication",
                    icon="📱",
                    is_enabled=False,
                    config={"phone": ""}
                ),
                Plugin(
                    name="Stripe",
                    slug="stripe",
                    description="Process payments via Stripe",
                    category="finance",
                    icon="💳",
                    is_enabled=False,
                    config={"api_key": ""}
                ),
                Plugin(
                    name="YouTube",
                    slug="youtube",
                    description="Search and analyze YouTube content",
                    category="research",
                    icon="▶️",
                    is_enabled=False,
                    config={"api_key": ""}
                ),
                Plugin(
                    name="Twitter/X",
                    slug="twitter",
                    description="Post and read Twitter/X content",
                    category="social",
                    icon="🐦",
                    is_enabled=False,
                    config={"api_key": ""}
                ),
                Plugin(
                    name="Shopify",
                    slug="shopify",
                    description="Manage your Shopify store",
                    category="ecommerce",
                    icon="🛍️",
                    is_enabled=False,
                    config={"store_url": "", "api_key": ""}
                ),
            ]
            db.add_all(plugins)
            db.commit()
            print("✅ Default plugins created!")

    finally:
        db.close()