"""
Database models for the Math Agent system
"""
import uuid
from datetime import datetime
from typing import Optional, Any, Dict, List
from sqlalchemy import Column, String, DateTime, Text, JSON, ForeignKey, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get database connection string
DB_CONNECTION_STRING = os.getenv("DB_CONNECTION_STRING", "sqlite:///math_agent.db")

# Create SQLAlchemy engine and session
engine = create_engine(DB_CONNECTION_STRING)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()

class Interaction(Base):
    """Model for storing math question interactions"""
    __tablename__ = "interactions"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    question = Column(Text, nullable=False)
    generated_solution = Column(JSON, nullable=True)  # Store solution steps as JSON
    source = Column(String, nullable=False)  # "knowledge_base", "web_search", "web_search_failed"
    kb_query = Column(Text, nullable=True)  # Query used for VectorDB search
    web_search_query = Column(Text, nullable=True)  # Query used for Web Search
    web_search_results = Column(JSON, nullable=True)  # Raw web search results
    context_used = Column(Text, nullable=True)  # Context used for generation
    llm_model = Column(String, nullable=True)  # Name of LLM model used
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    # Relationship with the Feedback model (one-to-many)
    feedback = relationship("Feedback", back_populates="interaction", cascade="all, delete-orphan")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary"""
        return {
            "interaction_id": self.id,
            "question": self.question,
            "solution": self.generated_solution,
            "source": self.source,
            "timestamp": self.timestamp.isoformat()
        }
    

class Feedback(Base):
    """Model for storing user feedback on solutions"""
    __tablename__ = "feedback"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    interaction_id = Column(String, ForeignKey("interactions.id"), nullable=False)
    feedback_type = Column(String, nullable=False)  # "helpful", "needs_improvement", "incorrect", etc.
    notes = Column(Text, nullable=True)  # Additional comments
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    # Relationship with the Interaction model
    interaction = relationship("Interaction", back_populates="feedback")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary"""
        return {
            "feedback_id": self.id,
            "interaction_id": self.interaction_id,
            "feedback_type": self.feedback_type,
            "notes": self.notes,
            "timestamp": self.timestamp.isoformat()
        }


# Create all tables
def init_db():
    """Initialize the database tables"""
    Base.metadata.create_all(bind=engine)
    

def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        return db
    finally:
        db.close() 