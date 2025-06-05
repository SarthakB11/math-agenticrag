"""
AI Gateway for input and output validation
"""
import re
import logging
from typing import List, Set, Dict, Any, Optional
from langchain_google_genai import GoogleGenerativeAI
from app.config import CONFIG

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AIGateway:
    """
    AI Gateway with guardrails to ensure all interactions are focused on mathematics
    and maintain safety and privacy. Acts as the entry and exit point for all user 
    interactions with the system.
    """
    
    def __init__(self):
        """Initialize the AI Gateway"""
        # Keywords related to math topics - used for basic filtering
        self.math_keywords: Set[str] = {
            "math", "algebra", "geometry", "calculus", "trigonometry", "equation", "formula",
            "solve", "simplify", "factor", "expand", "derivative", "integral", "function",
            "graph", "polynomial", "matrix", "vector", "number", "set", "probability", 
            "statistics", "mean", "median", "mode", "standard deviation", "variance",
            "theorem", "axiom", "proof", "angle", "triangle", "circle", "square",
            "rectangle", "polygon", "expression", "variable", "constant", "coefficient",
            "exponent", "logarithm", "base", "root", "square root", "cube root",
            "percentage", "ratio", "proportion", "limit", "sequence", "series", "summation",
            "factorial", "combination", "permutation", "binomial", "value", "divide", "multiply",
            "addition", "subtraction", "multiplication", "division", "fraction", "decimal"
        }
        
        # Prohibited keywords/patterns - topics to block
        self.prohibited_patterns: List[str] = [
            r"\b(sex|porn|explicit|nsfw|xxx)\b",
            r"\b(hack|exploit|steal|illegal)\b",
            r"\bhow\s+to\s+(make|create|build)\s+(bomb|explosive|weapon)",
            r"\bpersonal\s+(information|data|address|phone|email)\b",
            r"\bpassword\b",
            r"\bcredit\s+card\b",
            r"\bsocial\s+security\b"
        ]
        
        # Initialize LLM for advanced classification if needed
        # (Lightweight models should be used here to minimize latency and costs)
        self.llm = None
        api_key = CONFIG["llm"].get("api_key")
        if api_key:
            try:
                self.llm = GoogleGenerativeAI(
                    api_key=api_key,
                    model="gemini-2.0-flash",
                    temperature=0.0,
                    max_output_tokens=100
                )
            except Exception as e:
                logger.warning(f"Failed to initialize LLM for gateway: {str(e)}")
                self.llm = None
    
    def validate_input(self, input_text: str) -> bool:
        """
        Validate user input to ensure it's a mathematical question and doesn't contain
        prohibited content.
        
        Args:
            input_text: The user's input text
            
        Returns:
            bool: True if the input is valid, False otherwise
        """
        if not input_text or input_text.strip() == "":
            logger.info("Empty input rejected")
            return False
        
        # Check for prohibited content
        for pattern in self.prohibited_patterns:
            if re.search(pattern, input_text, re.IGNORECASE):
                logger.warning(f"Input rejected due to prohibited content: {pattern}")
                return False
        
        # Simple keyword check for math relevance
        # Count math-related keywords in the input
        word_count = len(re.findall(r'\b\w+\b', input_text.lower()))
        if word_count == 0:
            logger.info("Input rejected: No valid words found")
            return False
        
        # Check for mathematical symbols as a strong indicator
        math_symbols_pattern = r'[\+\-\*\/\^\=\<\>\(\)\[\]\{\}\.\d]'
        has_math_symbols = bool(re.search(math_symbols_pattern, input_text))
        
        # Count math keywords
        math_keyword_count = sum(1 for keyword in self.math_keywords 
                               if re.search(rf'\b{re.escape(keyword)}\b', input_text, re.IGNORECASE))
        
        # If we have math symbols or keywords, it's likely math-related
        if has_math_symbols or math_keyword_count > 0:
            logger.info(f"Input accepted with {math_keyword_count} math keywords and math symbols: {has_math_symbols}")
            return True
        
        # For uncertain cases, use LLM for classification if available
        if self.llm and not (has_math_symbols or math_keyword_count >= 1):
            try:
                prompt = f"""
                Classify the following query as either 'MATH' or 'NOT_MATH'. 
                The query should only be classified as 'MATH' if it's directly related to 
                mathematical concepts, problems, or education.
                
                Query: {input_text}
                
                Classification:
                """
                
                response = self.llm.predict(prompt).strip()
                result = "MATH" in response.upper()
                logger.info(f"LLM classification for input: {response} -> {result}")
                return result
            except Exception as e:
                logger.error(f"Error during LLM classification: {str(e)}")
                # Fall back to basic check if LLM fails
                return math_keyword_count > 0
        
        # Default case: insufficient math relevance
        logger.info("Input rejected: Insufficient math relevance")
        return False
    
    def validate_output(self, output_text: Any) -> bool:
        """
        Validate the system's output to ensure it's appropriate and safe.
        
        Args:
            output_text: The generated output (may be string or structured data)
            
        Returns:
            bool: True if the output is valid, False otherwise
        """
        # Handle different output formats
        if isinstance(output_text, list):
            # Concatenate list items for validation
            text_to_validate = " ".join(str(item) for item in output_text)
        elif isinstance(output_text, dict):
            # Extract relevant fields for validation
            if "steps" in output_text:
                text_to_validate = " ".join(str(step) for step in output_text["steps"])
            elif "text" in output_text:
                text_to_validate = str(output_text["text"])
            else:
                text_to_validate = str(output_text)
        else:
            text_to_validate = str(output_text)
        
        # Check for prohibited content in output
        for pattern in self.prohibited_patterns:
            if re.search(pattern, text_to_validate, re.IGNORECASE):
                logger.warning(f"Output rejected due to prohibited content: {pattern}")
                return False
        
        # Basic validation passed
        return True 