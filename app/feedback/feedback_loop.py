"""
Feedback Loop module for Human-in-the-Loop learning
"""
import logging
from typing import List, Dict, Any, Optional, Tuple
from app.models.database import get_db, Feedback, Interaction
from app.config import CONFIG
import json
import datetime
import uuid
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FeedbackLoop:
    """
    Human-in-the-Loop feedback mechanism that collects, processes, and uses
    user feedback to refine the Math Agent's responses over time.
    """
    
    def __init__(self, feedback_log_path: Optional[str] = None):
        """
        Initialize the Feedback Loop
        
        Args:
            feedback_log_path: Path to store feedback logs (default: data/feedback_logs)
        """
        self.feedback_log_path = feedback_log_path or os.path.join("data", "feedback_logs")
        
        # Create feedback log directory if it doesn't exist
        os.makedirs(self.feedback_log_path, exist_ok=True)
        logger.info(f"Feedback logs will be stored in: {self.feedback_log_path}")
    
    def submit_feedback(self, interaction_id: str, feedback_type: str, notes: Optional[str] = None) -> Dict[str, Any]:
        """
        Submit feedback for a specific interaction
        
        Args:
            interaction_id: ID of the interaction
            feedback_type: Type of feedback ("helpful", "needs_improvement", "incorrect", etc.)
            notes: Additional notes/comments
            
        Returns:
            Dict: Result of the feedback submission
        """
        try:
            # Get database
            db = get_db()
            
            # Check if interaction exists
            interaction = Interaction.get_by_id(interaction_id)
            if not interaction:
                logger.warning(f"Tried to submit feedback for non-existent interaction: {interaction_id}")
                return {"success": False, "message": "Interaction not found"}
            
            # Create feedback record
            feedback_id = Feedback.create(
                interaction_id=interaction_id,
                feedback_type=feedback_type,
                notes=notes
            )
            
            # Also log feedback to file
            self._log_feedback_to_file(
                interaction_id=interaction_id,
                feedback_type=feedback_type,
                notes=notes,
                interaction_data={
                    "question": interaction["question"],
                    "solution": interaction["generated_solution"],
                    "source": interaction["source"]
                }
            )
            
            logger.info(f"Feedback submitted for interaction {interaction_id}: {feedback_type}")
            return {"success": True, "feedback_id": feedback_id}
            
        except Exception as e:
            logger.error(f"Error submitting feedback: {str(e)}")
            return {"success": False, "message": str(e)}
    
    def submit_detailed_feedback(self, interaction_id: str, feedback_text: str) -> Dict[str, Any]:
        """
        Submit detailed feedback text for a specific interaction
        
        Args:
            interaction_id: ID of the interaction
            feedback_text: Detailed feedback text from the user
            
        Returns:
            Dict: Result of the feedback submission
        """
        # Determine feedback type based on text (simple heuristic)
        feedback_type = "detailed"
        
        # Submit the feedback
        return self.submit_feedback(interaction_id, feedback_type, feedback_text)
    
    def _log_feedback_to_file(
        self, 
        interaction_id: str, 
        feedback_type: str, 
        notes: Optional[str], 
        interaction_data: Dict[str, Any]
    ) -> None:
        """
        Log feedback to a file for offline processing and model improvements
        
        Args:
            interaction_id: ID of the interaction
            feedback_type: Type of feedback
            notes: Additional notes
            interaction_data: Data about the interaction
        """
        try:
            # Create a log entry
            log_entry = {
                "interaction_id": interaction_id,
                "feedback_type": feedback_type,
                "notes": notes,
                "interaction": interaction_data,
                "timestamp": datetime.datetime.utcnow().isoformat()
            }
            
            # Create a log file name
            filename = f"{interaction_id}_{feedback_type}_{datetime.datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
            filepath = os.path.join(self.feedback_log_path, filename)
            
            # Write to file
            with open(filepath, 'w') as f:
                json.dump(log_entry, f, indent=2)
            
            logger.info(f"Feedback logged to file: {filepath}")
            
        except Exception as e:
            logger.error(f"Error logging feedback to file: {str(e)}")
    
    def get_recent_feedback(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get recent feedback for analysis
        
        Args:
            limit: Maximum number of feedback items to retrieve
            
        Returns:
            List[Dict]: Recent feedback items
        """
        try:
            # Get database
            db = get_db()
            
            # Query recent feedback using MongoDB
            feedback_collection = db.feedback
            feedback_items = list(feedback_collection.find().sort("timestamp", -1).limit(limit))
            
            # Convert to list of dictionaries
            result = []
            for item in feedback_items:
                # Get associated interaction
                interaction = Interaction.get_by_id(item["interaction_id"])
                
                feedback_dict = Feedback.to_dict(item)
                feedback_dict["interaction"] = Interaction.to_dict(interaction) if interaction else {}
                
                result.append(feedback_dict)
            
            return result
            
        except Exception as e:
            logger.error(f"Error retrieving recent feedback: {str(e)}")
            return []
    
    def analyze_feedback(self) -> Dict[str, Any]:
        """
        Analyze feedback to identify trends and improvement areas
        
        Returns:
            Dict: Analysis results
        """
        try:
            # Get database
            db = get_db()
            feedback_collection = db.feedback
            interactions_collection = db.interactions
            
            # Get feedback counts by type
            feedback_counts = {}
            for feedback_type in ["helpful", "needs_improvement", "incorrect", "detailed"]:
                count = feedback_collection.count_documents({"feedback_type": feedback_type})
                feedback_counts[feedback_type] = count
            
            # Get source distribution
            source_counts = {}
            source_pipeline = [
                {"$group": {"_id": "$source", "count": {"$sum": 1}}}
            ]
            source_results = list(interactions_collection.aggregate(source_pipeline))
            for result in source_results:
                source_counts[result["_id"]] = result["count"]
            
            # Calculate success rate (% of helpful feedback)
            total_feedback = sum(feedback_counts.values())
            helpful_feedback = feedback_counts.get("helpful", 0)
            success_rate = (helpful_feedback / total_feedback) * 100 if total_feedback > 0 else 0
            
            analysis = {
                "feedback_counts": feedback_counts,
                "source_distribution": source_counts,
                "success_rate": success_rate,
                "total_interactions": interactions_collection.count_documents({}),
                "total_feedback": total_feedback
            }
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing feedback: {str(e)}")
            return {}
    
    def integrate_feedback_dspy(self) -> Dict[str, Any]:
        """
        Integrate feedback using DSPy for model optimization (to be implemented)
        
        Returns:
            Dict: Integration results
        """
        # This is a placeholder for DSPy integration - would require additional implementation
        try:
            logger.info("DSPy feedback integration requested (not yet implemented)")
            return {"success": False, "message": "DSPy integration not yet implemented"}
        except Exception as e:
            logger.error(f"Error in DSPy feedback integration: {str(e)}")
            return {"success": False, "message": str(e)} 