"""
Database models for the Math Agent system
"""
import uuid
from datetime import datetime
from typing import Optional, Any, Dict, List
import os
from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.database import Database
from pymongo.collection import Collection

# Load environment variables
load_dotenv()

# Get database connection string
DB_CONNECTION_STRING = os.getenv("DB_CONNECTION_STRING", "mongodb://localhost:27017/math_agent")

# Create MongoDB client
client = MongoClient(DB_CONNECTION_STRING)
db = client.get_database("math_agent")

# Collections
interactions_collection = db.interactions
feedback_collection = db.feedback

class Interaction:
    """Model for storing math question interactions"""
    
    @staticmethod
    def create(
        question: str,
        generated_solution: Optional[Dict[str, Any]] = None,
        source: str = "knowledge_base",
        kb_query: Optional[str] = None,
        web_search_query: Optional[str] = None,
        web_search_results: Optional[Dict[str, Any]] = None,
        context_used: Optional[str] = None,
        llm_model: Optional[str] = None
    ) -> str:
        """Create a new interaction record"""
        interaction_id = str(uuid.uuid4())
        interactions_collection.insert_one({
            "_id": interaction_id,
            "question": question,
            "generated_solution": generated_solution,
            "source": source,
            "kb_query": kb_query,
            "web_search_query": web_search_query,
            "web_search_results": web_search_results,
            "context_used": context_used,
            "llm_model": llm_model,
            "timestamp": datetime.utcnow()
        })
        return interaction_id
    
    @staticmethod
    def get_by_id(interaction_id: str) -> Optional[Dict[str, Any]]:
        """Get interaction by ID"""
        result = interactions_collection.find_one({"_id": interaction_id})
        return result
    
    @staticmethod
    def to_dict(interaction: Dict[str, Any]) -> Dict[str, Any]:
        """Convert MongoDB document to dictionary"""
        return {
            "interaction_id": interaction["_id"],
            "question": interaction["question"],
            "solution": interaction["generated_solution"],
            "source": interaction["source"],
            "timestamp": interaction["timestamp"].isoformat()
        }
    

class Feedback:
    """Model for storing user feedback on solutions"""
    
    @staticmethod
    def create(
        interaction_id: str,
        feedback_type: str,
        notes: Optional[str] = None
    ) -> str:
        """Create a new feedback record"""
        feedback_id = str(uuid.uuid4())
        feedback_collection.insert_one({
            "_id": feedback_id,
            "interaction_id": interaction_id,
            "feedback_type": feedback_type,
            "notes": notes,
            "timestamp": datetime.utcnow()
        })
        return feedback_id
    
    @staticmethod
    def get_by_id(feedback_id: str) -> Optional[Dict[str, Any]]:
        """Get feedback by ID"""
        result = feedback_collection.find_one({"_id": feedback_id})
        return result
    
    @staticmethod
    def get_by_interaction_id(interaction_id: str) -> List[Dict[str, Any]]:
        """Get all feedback for an interaction"""
        results = list(feedback_collection.find({"interaction_id": interaction_id}))
        return results
    
    @staticmethod
    def to_dict(feedback: Dict[str, Any]) -> Dict[str, Any]:
        """Convert MongoDB document to dictionary"""
        return {
            "feedback_id": feedback["_id"],
            "interaction_id": feedback["interaction_id"],
            "feedback_type": feedback["feedback_type"],
            "notes": feedback["notes"],
            "timestamp": feedback["timestamp"].isoformat()
        }


# Initialize the database
def init_db():
    """Initialize the database collections with indexes"""
    interactions_collection.create_index("timestamp")
    feedback_collection.create_index("interaction_id")
    

def get_db() -> Database:
    """Get database instance"""
    return db 