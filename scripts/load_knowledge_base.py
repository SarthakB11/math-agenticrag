#!/usr/bin/env python3
"""
Script to load sample data into the knowledge base
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

# Sample math knowledge data
SAMPLE_DATA = [
    {
        "text": "The quadratic formula is used to solve quadratic equations in the form ax² + bx + c = 0. The formula is x = (-b ± √(b² - 4ac)) / 2a, where b² - 4ac is called the discriminant.",
        "metadata": {
            "topic": "algebra",
            "subtopic": "quadratic_equations",
            "difficulty": "medium"
        }
    },
    {
        "text": "The derivative of a function f(x) is defined as the limit of the ratio of the change in the function value to the change in the independent variable, as the change in the independent variable approaches zero. Symbolically, f'(x) = lim(h→0) [f(x+h) - f(x)]/h.",
        "metadata": {
            "topic": "calculus",
            "subtopic": "derivatives",
            "difficulty": "medium"
        }
    },
    {
        "text": "The Pythagorean theorem states that in a right triangle, the square of the length of the hypotenuse equals the sum of the squares of the lengths of the other two sides. If a and b are the legs and c is the hypotenuse, then a² + b² = c².",
        "metadata": {
            "topic": "geometry",
            "subtopic": "triangles",
            "difficulty": "easy"
        }
    },
    {
        "text": "Integration is the inverse of differentiation. The indefinite integral of a function f(x) is written as ∫f(x)dx and represents the antiderivative of f(x). The definite integral of f(x) from a to b is written as ∫(a to b)f(x)dx and represents the area under the curve of f(x) from x=a to x=b.",
        "metadata": {
            "topic": "calculus",
            "subtopic": "integration",
            "difficulty": "medium"
        }
    },
    {
        "text": "The law of sines relates the sides of a triangle to the sines of the opposite angles. In a triangle with sides a, b, c and opposite angles A, B, C, the law states that a/sin(A) = b/sin(B) = c/sin(C).",
        "metadata": {
            "topic": "trigonometry",
            "subtopic": "triangles",
            "difficulty": "medium"
        }
    },
    {
        "text": "The derivative of a constant is 0. For any constant k, d/dx(k) = 0.",
        "metadata": {
            "topic": "calculus",
            "subtopic": "derivatives",
            "difficulty": "easy"
        }
    },
    {
        "text": "The derivative of x^n is nx^(n-1) for any real number n. For example, d/dx(x^3) = 3x^2.",
        "metadata": {
            "topic": "calculus",
            "subtopic": "derivatives",
            "difficulty": "easy"
        }
    },
    {
        "text": "The chain rule is used to find the derivative of a composite function. If y = f(g(x)), then dy/dx = (df/dg) * (dg/dx).",
        "metadata": {
            "topic": "calculus",
            "subtopic": "derivatives",
            "difficulty": "medium"
        }
    },
    {
        "text": "The product rule states that if f and g are differentiable functions, then the derivative of their product is (f * g)' = f' * g + f * g'.",
        "metadata": {
            "topic": "calculus",
            "subtopic": "derivatives",
            "difficulty": "medium"
        }
    },
    {
        "text": "The quotient rule states that if f and g are differentiable functions, then the derivative of their quotient is (f/g)' = (f' * g - f * g') / g^2.",
        "metadata": {
            "topic": "calculus",
            "subtopic": "derivatives",
            "difficulty": "medium"
        }
    }
]

def main():
    """Load sample data into the knowledge base"""
    try:
        # Initialize VectorDB
        vector_db = VectorDB(
            url=os.getenv("VECTOR_DB_URL", "localhost"),
            port=int(os.getenv("VECTOR_DB_PORT", "6333")),
            collection_name=os.getenv("VECTOR_DB_COLLECTION", "math_knowledge_base")
        )
        
        logger.info(f"Loading {len(SAMPLE_DATA)} sample items into the knowledge base...")
        
        # Load sample data
        for i, item in enumerate(SAMPLE_DATA, 1):
            text = item["text"]
            metadata = item["metadata"]
            
            # Add to knowledge base
            point_id = vector_db.add_to_kb(text, metadata)
            
            logger.info(f"Added item {i}/{len(SAMPLE_DATA)} with ID: {point_id}")
        
        logger.info("Sample data loaded successfully!")
        
        # Check if custom data directory exists
        custom_data_dir = os.path.join(os.path.dirname(__file__), "..", "data", "kb_data")
        if os.path.exists(custom_data_dir):
            # Look for JSON files in the data directory
            json_files = glob.glob(os.path.join(custom_data_dir, "*.json"))
            
            if json_files:
                logger.info(f"Found {len(json_files)} custom data files, loading...")
                
                for json_file in json_files:
                    try:
                        with open(json_file, 'r') as f:
                            custom_data = json.load(f)
                        
                        # Check if it's a list of items or a single item
                        if isinstance(custom_data, list):
                            for item in custom_data:
                                if "text" in item and "metadata" in item:
                                    vector_db.add_to_kb(item["text"], item["metadata"])
                        elif isinstance(custom_data, dict) and "text" in custom_data and "metadata" in custom_data:
                            vector_db.add_to_kb(custom_data["text"], custom_data["metadata"])
                        
                        logger.info(f"Loaded custom data from {os.path.basename(json_file)}")
                    except Exception as e:
                        logger.error(f"Error loading custom data from {json_file}: {str(e)}")
            else:
                logger.info("No custom data files found.")
        
    except Exception as e:
        logger.error(f"Error loading sample data: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 