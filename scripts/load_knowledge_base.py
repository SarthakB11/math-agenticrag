#!/usr/bin/env python3
"""
Script to load real math problems into the knowledge base
"""
import os
import sys
import logging
import json
import glob

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.kb.vector_db import VectorDB
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    """Load real math problems into the knowledge base"""
    try:
        # Initialize VectorDB
        vector_db = VectorDB(
            url=os.getenv("VECTOR_DB_URL", "localhost"),
            port=int(os.getenv("VECTOR_DB_PORT", "6333")),
            collection_name=os.getenv("VECTOR_DB_COLLECTION", "math_knowledge_base")
        )
        
        # Load real dataset from dataset.json
        dataset_path = os.path.join(os.path.dirname(__file__), "..", "data", "kb_data", "data", "dataset.json")
        
        if os.path.exists(dataset_path):
            logger.info(f"Loading real dataset from {dataset_path}...")
            
            try:
                with open(dataset_path, 'r') as f:
                    dataset = json.load(f)
                
                # Filter only math problems
                math_problems = [problem for problem in dataset if problem.get("subject") == "math"]
                
                logger.info(f"Found {len(math_problems)} math problems out of {len(dataset)} total problems, loading into KB...")
                
                for i, problem in enumerate(math_problems, 1):
                    # Extract problem information
                    question_text = problem.get("question", "")
                    question_type = problem.get("type", "")
                    gold_answer = problem.get("gold", "")
                    description = problem.get("description", "")
                    
                    # Create text with problem information
                    text = f"Problem: {question_text}\nAnswer: {gold_answer}"
                    
                    # Create metadata
                    metadata = {
                        "subject": "math",
                        "type": question_type,
                        "description": description,
                        "difficulty": "medium"  # Default difficulty
                    }
                    
                    # Add to knowledge base
                    point_id = vector_db.add_to_kb(text, metadata)
                    
                    if i % 25 == 0:
                        logger.info(f"Added {i}/{len(math_problems)} math problems to KB")
                
                logger.info(f"Successfully loaded all {len(math_problems)} math problems into the knowledge base!")
                
            except Exception as e:
                logger.error(f"Error loading dataset.json: {str(e)}")
                sys.exit(1)
        else:
            logger.error(f"Dataset file not found at {dataset_path}")
            sys.exit(1)
        
        # Also check for few_shot_examples.json
        few_shot_path = os.path.join(os.path.dirname(__file__), "..", "data", "kb_data", "data", "few_shot_examples.json")
        
        if os.path.exists(few_shot_path):
            logger.info(f"Loading few-shot examples from {few_shot_path}...")
            
            try:
                with open(few_shot_path, 'r') as f:
                    few_shot_data = json.load(f)
                
                # Process few-shot examples for math only
                if "math" in few_shot_data:
                    math_examples = few_shot_data["math"]
                    logger.info(f"Found {len(math_examples)} types of math examples")
                    
                    for q_type, content in math_examples.items():
                        problem = content.get("problem", "")
                        solution = content.get("solution", "")
                        
                        text = f"Problem: {problem}\nSolution: {solution}"
                        
                        metadata = {
                            "subject": "math",
                            "type": q_type,
                            "is_few_shot": True,
                            "difficulty": "medium"
                        }
                        
                        vector_db.add_to_kb(text, metadata)
                    
                    logger.info("Successfully loaded math few-shot examples into the knowledge base!")
                else:
                    logger.warning("No math examples found in few_shot_examples.json")
                
            except Exception as e:
                logger.error(f"Error loading few_shot_examples.json: {str(e)}")
        
    except Exception as e:
        logger.error(f"Error loading knowledge base data: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 