"""
Generation Agent for the Math Agent system
"""
import logging
import os
from typing import List, Dict, Any, Optional, Union
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain import PromptTemplate, LLMChain
from langchain.schema import HumanMessage, SystemMessage
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

class GenerationAgent:
    """
    The Generation Agent utilizes a Large Language Model (LLM) to synthesize information
    from either retrieved Knowledge Base chunks or extracted web content into a step-by-step,
    simplified mathematical solution.
    """
    
    def __init__(self, api_key: Optional[str] = None, model_name: str = "gemini-pro"):
        """
        Initialize the Generation Agent
        
        Args:
            api_key: API key for the LLM (default: from env)
            model_name: The model to use (default: gemini-pro)
        """
        self.api_key = api_key or os.getenv("LLM_API_KEY", "")
        self.model_name = model_name
        
        if not self.api_key:
            logger.warning("No LLM API key provided, generation will not function")
            self.llm = None
        else:
            try:
                # Initialize the LLM
                self.llm = ChatGoogleGenerativeAI(
                    api_key=self.api_key,
                    model=self.model_name,
                    temperature=0.2  # Lower temperature for more deterministic, factual responses
                )
                logger.info(f"LLM initialized with model: {model_name}")
            except Exception as e:
                logger.error(f"Failed to initialize LLM: {str(e)}")
                self.llm = None
    
    def generate_from_kb(self, question: str, kb_context: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate a step-by-step solution using Knowledge Base content
        
        Args:
            question: The math question
            kb_context: The retrieved knowledge base items
            
        Returns:
            Dict: Generated solution with steps
        """
        if not self.llm:
            logger.error("LLM not initialized, cannot generate response")
            return {"error": "LLM not initialized"}
        
        try:
            # Extract text from KB context
            context_text = ""
            for item in kb_context:
                text = item.get("text", "")
                score = item.get("score", 0)
                context_text += f"[Knowledge Base Entry (relevance: {score:.2f})]\n{text}\n\n"
            
            # System message prompting LLM to act as a math professor
            system_prompt = """You are an expert math professor with a knack for providing clear, step-by-step explanations to math problems. 
Your goal is to help students understand not just the answer, but the process of solving the problem.

When answering questions:
1. Break down the solution into clear, logical steps
2. Explain each step thoroughly, but in simple language
3. Use relevant mathematical concepts from the provided knowledge base
4. Simplify complex ideas using analogies or visual descriptions where appropriate
5. Double-check calculations for accuracy
6. Include the final answer clearly labeled

If the knowledge base doesn't contain information directly related to the problem, use your mathematical knowledge but
make sure your reasoning is sound. Never invent incorrect mathematical facts or procedures.

IMPORTANT: Format your response as a list of steps, with each step clearly explaining one part of the solution process.
"""
            
            # User message with question and context
            user_prompt = f"""
Question: {question}

Here is relevant information from my knowledge base that may help answer this question:

{context_text}

Please provide a step-by-step solution to this math problem, explaining each step clearly as if teaching a student.
"""
            
            # Generate the response
            response = self.llm.invoke([
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt)
            ])
            
            # Extract and format the solution steps
            solution_text = response.content
            
            # Process the solution to extract steps
            steps = self._extract_steps(solution_text)
            
            logger.info(f"Generated solution with {len(steps)} steps from KB content")
            
            return {
                "steps": steps,
                "full_text": solution_text,
                "source": "knowledge_base"
            }
            
        except Exception as e:
            logger.error(f"Error generating solution from KB context: {str(e)}")
            return {"error": str(e)}
    
    def generate_from_web(self, question: str, web_content: str) -> Dict[str, Any]:
        """
        Generate a step-by-step solution using web content
        
        Args:
            question: The math question
            web_content: The extracted web content
            
        Returns:
            Dict: Generated solution with steps
        """
        if not self.llm:
            logger.error("LLM not initialized, cannot generate response")
            return {"error": "LLM not initialized"}
        
        try:
            # System message prompting LLM to act as a math professor
            system_prompt = """You are an expert math professor with a knack for providing clear, step-by-step explanations to math problems. 
Your goal is to help students understand not just the answer, but the process of solving the problem.

When answering questions:
1. Break down the solution into clear, logical steps
2. Explain each step thoroughly, but in simple language
3. Use relevant mathematical concepts from the provided web content
4. Simplify complex ideas using analogies or visual descriptions where appropriate
5. Double-check calculations for accuracy
6. Include the final answer clearly labeled

IMPORTANT: 
- Format your response as a list of steps, with each step clearly explaining one part of the solution process.
- If the web content doesn't contain sufficient information to solve the problem accurately, explain what you do know based on the content, then state that you don't have enough information to provide a complete solution.
- Do NOT make up or hallucinate information that isn't present in the web content.
- If you cannot provide a reliable solution, clearly say so rather than giving potentially incorrect information.
"""
            
            # User message with question and context
            user_prompt = f"""
Question: {question}

Here is relevant information from my web search that may help answer this question:

{web_content}

Please provide a step-by-step solution to this math problem, explaining each step clearly as if teaching a student.
If the information isn't sufficient to solve the problem accurately, explain what you know and indicate that you cannot provide a complete solution.
"""
            
            # Generate the response
            response = self.llm.invoke([
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt)
            ])
            
            # Extract and format the solution steps
            solution_text = response.content
            
            # Check if the solution indicates inability to answer
            cannot_answer_patterns = [
                "cannot provide a complete solution",
                "don't have enough information",
                "insufficient information",
                "not enough context",
                "cannot solve this problem",
                "unable to provide a solution"
            ]
            
            cannot_answer = any(pattern.lower() in solution_text.lower() for pattern in cannot_answer_patterns)
            
            if cannot_answer:
                logger.info("Generated response indicates inability to answer")
                return {
                    "steps": ["I'm sorry, but I don't have enough information to provide a complete solution to this problem."],
                    "full_text": solution_text,
                    "source": "web_search_failed"
                }
            
            # Process the solution to extract steps
            steps = self._extract_steps(solution_text)
            
            logger.info(f"Generated solution with {len(steps)} steps from web content")
            
            return {
                "steps": steps,
                "full_text": solution_text,
                "source": "web_search"
            }
            
        except Exception as e:
            logger.error(f"Error generating solution from web content: {str(e)}")
            return {"error": str(e)}
    
    def generate_cannot_answer(self, question: str) -> Dict[str, Any]:
        """
        Generate a "cannot answer" response when both KB and web search fail
        
        Args:
            question: The math question
            
        Returns:
            Dict: Generated response
        """
        if not self.llm:
            logger.error("LLM not initialized, cannot generate response")
            return {
                "steps": ["I'm sorry, but I cannot provide a solution to this math problem at this time."],
                "source": "web_search_failed"
            }
        
        try:
            # System message
            system_prompt = """You are an expert math professor. You need to inform the student that you don't have enough information to solve their math problem completely. Be honest but encouraging."""
            
            # User message
            user_prompt = f"""
I couldn't find sufficient information to solve this math problem: "{question}"

Please generate a polite and helpful response explaining that you cannot provide a complete solution, but offering some general guidance if possible based on the type of problem. Include suggestions for how the student might approach this type of problem.
"""
            
            # Generate the response
            response = self.llm.invoke([
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt)
            ])
            
            # Use response as a single step
            steps = [response.content.strip()]
            
            logger.info("Generated 'cannot answer' response")
            
            return {
                "steps": steps,
                "source": "web_search_failed"
            }
            
        except Exception as e:
            logger.error(f"Error generating 'cannot answer' response: {str(e)}")
            return {
                "steps": ["I'm sorry, but I cannot provide a solution to this math problem at this time."],
                "source": "web_search_failed"
            }
    
    def _extract_steps(self, solution_text: str) -> List[str]:
        """
        Extract step-by-step solution from the generated text
        
        Args:
            solution_text: The full solution text
            
        Returns:
            List[str]: Extracted steps
        """
        # Try to extract numbered steps (most common format)
        import re
        
        # Look for numbered steps like "1.", "Step 1:", etc.
        step_patterns = [
            r"Step\s+(\d+)[\:\.]\s*(.*?)(?=Step\s+\d+[\:\.]|$)",  # "Step 1: ..."
            r"(\d+)[\:\.]\s*(.*?)(?=\d+[\:\.]|$)",  # "1. ..."
            r"Step\s+(\d+)\s*(.*?)(?=Step\s+\d+|$)",  # "Step 1 ..."
        ]
        
        for pattern in step_patterns:
            matches = re.findall(pattern, solution_text, re.DOTALL | re.IGNORECASE)
            if matches:
                steps = [step[1].strip() if isinstance(step, tuple) and len(step) > 1 else step.strip() 
                         for step in matches]
                steps = [step for step in steps if step]  # Remove empty steps
                
                if steps:
                    return steps
        
        # If no structured steps found, split by double newlines (paragraphs)
        paragraphs = [p.strip() for p in solution_text.split("\n\n") if p.strip()]
        if len(paragraphs) > 1:
            return paragraphs
        
        # Fallback: Split by single newlines
        lines = [line.strip() for line in solution_text.split("\n") if line.strip()]
        if len(lines) > 1:
            return lines
        
        # Last resort: Return the whole text as a single step
        return [solution_text.strip()] 