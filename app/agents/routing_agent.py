"""
Routing Agent for the Math Agent system
"""
import logging
import uuid
from typing import List, Dict, Any, Optional, Tuple
import os
from app.kb.vector_db import VectorDB
from app.web_search.search_agent import WebSearchAgent
from app.agents.generation_agent import GenerationAgent
from app.models.database import get_db, Interaction
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

class RoutingAgent:
    """
    The Routing Agent analyzes the incoming query and determines the appropriate next step:
    Knowledge Base search or Web Search. It orchestrates the entire solution generation workflow.
    """
    
    def __init__(
        self, 
        vector_db: VectorDB,
        web_search_agent: WebSearchAgent,
        generation_agent: GenerationAgent,
        kb_similarity_threshold: float = 0.70
    ):
        """
        Initialize the Routing Agent
        
        Args:
            vector_db: Vector Database instance
            web_search_agent: Web Search Agent instance
            generation_agent: Generation Agent instance
            kb_similarity_threshold: Threshold for KB match (0-1)
        """
        self.vector_db = vector_db
        self.web_search_agent = web_search_agent
        self.generation_agent = generation_agent
        self.kb_similarity_threshold = kb_similarity_threshold
        logger.info(f"Routing Agent initialized with KB threshold: {kb_similarity_threshold}")
    
    def process(self, question: str) -> Dict[str, Any]:
        """
        Process a question, route to the appropriate source, and generate a solution
        
        Args:
            question: The math question to answer
            
        Returns:
            Dict: Solution, source, and interaction ID
        """
        # Generate a unique ID for this interaction
        interaction_id = str(uuid.uuid4())
        logger.info(f"Processing question with ID {interaction_id}: {question}")
        
        try:
            # First try Knowledge Base
            kb_results, found_good_match = self.vector_db.search(
                query=question,
                limit=5,
                threshold=self.kb_similarity_threshold
            )
            
            # Generate solution based on routing decision
            if found_good_match and kb_results:
                logger.info(f"KB search found good match for question: {question}")
                result = self.generation_agent.generate_from_kb(question, kb_results)
                source = "knowledge_base"
                
                # Extract context used for logging/storage
                context_used = "\n\n".join([item.get("text", "") for item in kb_results])
                
                # Store data in database
                self._store_interaction(
                    interaction_id=interaction_id,
                    question=question,
                    solution=result.get("steps", []),
                    source=source,
                    kb_query=question,
                    context_used=context_used[:1000]  # Limit to avoid overly large DB entries
                )
                
                # Return the result
                return {
                    "interaction_id": interaction_id,
                    "question": question,
                    "solution": result.get("steps", []),
                    "source": source
                }
            else:
                # Try Web Search
                logger.info(f"No good KB match, trying web search for question: {question}")
                web_results = self.web_search_agent.search(question)
                
                if web_results:
                    # Extract and process web content
                    processed_content = self.web_search_agent.process_results(web_results, question)
                    
                    if processed_content:
                        # Generate solution from web content
                        result = self.generation_agent.generate_from_web(question, processed_content)
                        source = result.get("source", "web_search")  # Could be "web_search" or "web_search_failed"
                        
                        # Store data in database
                        self._store_interaction(
                            interaction_id=interaction_id,
                            question=question,
                            solution=result.get("steps", []),
                            source=source,
                            web_search_query=question,
                            web_search_results=web_results[:2],  # Store only top results
                            context_used=processed_content[:1000]  # Limit to avoid overly large DB entries
                        )
                        
                        # Return the result
                        return {
                            "interaction_id": interaction_id,
                            "question": question,
                            "solution": result.get("steps", []),
                            "source": source
                        }
                    else:
                        # Web extraction failed
                        logger.warning(f"Web extraction failed for question: {question}")
                        result = self.generation_agent.generate_cannot_answer(question)
                        
                        # Store data in database
                        self._store_interaction(
                            interaction_id=interaction_id,
                            question=question,
                            solution=result.get("steps", []),
                            source="web_search_failed",
                            web_search_query=question,
                            web_search_results=web_results[:2]  # Store only top results
                        )
                        
                        # Return the result
                        return {
                            "interaction_id": interaction_id,
                            "question": question,
                            "solution": result.get("steps", []),
                            "source": "web_search_failed"
                        }
                else:
                    # Web search returned no results
                    logger.warning(f"Web search returned no results for question: {question}")
                    result = self.generation_agent.generate_cannot_answer(question)
                    
                    # Store data in database
                    self._store_interaction(
                        interaction_id=interaction_id,
                        question=question,
                        solution=result.get("steps", []),
                        source="web_search_failed",
                        web_search_query=question
                    )
                    
                    # Return the result
                    return {
                        "interaction_id": interaction_id,
                        "question": question,
                        "solution": result.get("steps", []),
                        "source": "web_search_failed"
                    }
        
        except Exception as e:
            logger.error(f"Error processing question: {str(e)}")
            
            # Return error response
            return {
                "interaction_id": interaction_id,
                "question": question,
                "solution": ["I'm sorry, but an error occurred while processing your question. Please try again later."],
                "source": "error",
                "error": str(e)
            }
    
    def _store_interaction(
        self,
        interaction_id: str,
        question: str,
        solution: List[str],
        source: str,
        kb_query: Optional[str] = None,
        web_search_query: Optional[str] = None,
        web_search_results: Optional[List[Dict[str, Any]]] = None,
        context_used: Optional[str] = None
    ) -> None:
        """
        Store interaction data in the database
        
        Args:
            interaction_id: Unique ID for this interaction
            question: The math question
            solution: The generated solution steps
            source: Source of the answer ("knowledge_base", "web_search", "web_search_failed")
            kb_query: Query used for KB search
            web_search_query: Query used for web search
            web_search_results: Raw web search results
            context_used: Context used for generation
        """
        try:
            # Get database session
            db = get_db()
            
            # Create new interaction record
            interaction = Interaction(
                id=interaction_id,
                question=question,
                generated_solution=solution,
                source=source,
                kb_query=kb_query,
                web_search_query=web_search_query,
                web_search_results=web_search_results,
                context_used=context_used,
                llm_model=self.generation_agent.model_name if self.generation_agent else None
            )
            
            # Add to database
            db.add(interaction)
            db.commit()
            
            logger.info(f"Stored interaction {interaction_id} in database")
            
        except Exception as e:
            logger.error(f"Error storing interaction in database: {str(e)}")
            # Continue execution even if database storage fails 