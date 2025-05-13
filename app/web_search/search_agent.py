"""
Web Search Agent and Content Extraction
"""
import logging
import requests
from typing import List, Dict, Any, Optional
import os
import re
import json
from bs4 import BeautifulSoup
import trafilatura
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

class WebSearchAgent:
    """
    Agent for handling web search and content extraction
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the Web Search Agent
        
        Args:
            api_key: API key for the search API (default: from env)
        """
        self.api_key = api_key or os.getenv("SEARCH_API_KEY", "")
        if not self.api_key:
            logger.warning("No search API key provided, web search will not function")
        
        # Educational domains preference
        self.preferred_domains = [
            "khanacademy.org",
            "mathsisfun.com",
            "purplemath.com",
            "mathworld.wolfram.com",
            "math.stackexchange.com",
            "brilliant.org",
            "en.wikipedia.org",
            "desmos.com",
            "wolframalpha.com",
            "symbolab.com",
            "mathpages.com",
            "mathjax.org",
            "mathcenter.com",
            "mathisfun.com",
            ".edu",  # Educational institutions
        ]
    
    def formulate_search_query(self, question: str) -> str:
        """
        Formulate an effective search query based on the math question
        
        Args:
            question: Original math question
            
        Returns:
            str: Formatted search query
        """
        # Preprocessing to improve search effectiveness
        # Remove "solve", "what is", "calculate", etc. at the beginning
        query = re.sub(r"^(solve|calculate|find|determine|what is|how to|evaluate|simplify)\s+", "", question.lower())
        
        # Add math-specific terms to improve search results
        query = f"math problem {query} solution"
        
        logger.info(f"Formulated search query: {query}")
        return query
    
    def search(self, question: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """
        Perform a web search for the given question
        
        Args:
            question: The math question to search for
            max_results: Maximum number of results to return
            
        Returns:
            List[Dict]: List of search results with metadata
        """
        if not self.api_key:
            logger.error("Cannot perform search without API key")
            return []
        
        # Formulate search query
        search_query = self.formulate_search_query(question)
        
        try:
            # Use Tavily API for search - fallback to simpler methods if not available
            try:
                import tavily
                from tavily import TavilyClient
                
                # Initialize Tavily client
                client = TavilyClient(api_key=self.api_key)
                
                # Perform search
                search_result = client.search(
                    query=search_query,
                    search_depth="basic",
                    max_results=max_results
                )
                
                # Process Tavily results
                results = []
                for item in search_result.get("results", []):
                    results.append({
                        "title": item.get("title", ""),
                        "url": item.get("url", ""),
                        "snippet": item.get("content", ""),
                        "score": 1.0,  # Default score as Tavily doesn't provide relevance scores
                        "source": "tavily"
                    })
                
                logger.info(f"Found {len(results)} results via Tavily API")
                return results
                
            except (ImportError, Exception) as e:
                logger.warning(f"Tavily search failed: {str(e)}. Falling back to Serper API.")
                
                # Fallback to Serper API
                headers = {
                    "X-API-KEY": self.api_key,
                    "Content-Type": "application/json"
                }
                
                payload = json.dumps({
                    "q": search_query,
                    "num": max_results
                })
                
                response = requests.post(
                    "https://google.serper.dev/search", 
                    headers=headers, 
                    data=payload
                )
                
                if response.status_code != 200:
                    logger.error(f"Search API returned status code {response.status_code}")
                    return []
                
                data = response.json()
                
                # Process results
                results = []
                for item in data.get("organic", []):
                    results.append({
                        "title": item.get("title", ""),
                        "url": item.get("link", ""),
                        "snippet": item.get("snippet", ""),
                        "score": 1.0,  # Default score
                        "source": "serper"
                    })
                
                logger.info(f"Found {len(results)} results via Serper API")
                return results
                
        except Exception as e:
            logger.error(f"Error performing web search: {str(e)}")
            return []
    
    def extract_content(self, url: str) -> str:
        """
        Extract the main content from a web page
        
        Args:
            url: URL to extract content from
            
        Returns:
            str: Extracted content
        """
        try:
            # Fetch web page
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            }
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code != 200:
                logger.warning(f"Failed to fetch {url}, status code: {response.status_code}")
                return ""
            
            # Try extraction with trafilatura (good at extracting main content)
            try:
                extracted = trafilatura.extract(response.text, output_format="text", include_tables=True)
                if extracted and len(extracted) > 100:  # Sanity check for content length
                    logger.info(f"Successfully extracted content from {url} using trafilatura")
                    return extracted
            except Exception as e:
                logger.warning(f"Trafilatura extraction failed for {url}: {str(e)}")
            
            # Fallback to BeautifulSoup
            soup = BeautifulSoup(response.text, "html.parser")
            
            # Remove non-content elements
            for element in soup(["script", "style", "nav", "footer", "header", "aside"]):
                element.decompose()
            
            # Get text
            text = soup.get_text(separator="\n", strip=True)
            
            # Clean up text (remove extra whitespace, etc.)
            text = re.sub(r"\n+", "\n", text)
            text = re.sub(r" +", " ", text)
            
            logger.info(f"Extracted content from {url} using BeautifulSoup")
            return text
            
        except Exception as e:
            logger.error(f"Error extracting content from {url}: {str(e)}")
            return ""
    
    def process_results(self, results: List[Dict[str, Any]], question: str) -> str:
        """
        Process search results to extract relevant content
        
        Args:
            results: List of search results
            question: Original math question
            
        Returns:
            str: Extracted and processed content
        """
        if not results:
            logger.warning("No search results to process")
            return ""
        
        # Filter and score results
        scored_results = []
        for result in results:
            # Calculate base score
            score = result.get("score", 1.0)
            
            # Prioritize educational domains
            url = result.get("url", "")
            if any(domain in url for domain in self.preferred_domains):
                score *= 1.5
            
            # Prioritize results with math keywords in title/snippet
            title = result.get("title", "")
            snippet = result.get("snippet", "")
            
            math_keywords = ["formula", "equation", "solution", "solve", "calculation", "math", "problem", "answer"]
            if any(keyword in title.lower() for keyword in math_keywords):
                score *= 1.2
            if any(keyword in snippet.lower() for keyword in math_keywords):
                score *= 1.1
                
            # Store updated score
            result["calculated_score"] = score
            scored_results.append(result)
        
        # Sort by score
        scored_results.sort(key=lambda x: x.get("calculated_score", 0), reverse=True)
        
        # Extract content from top results (max 2-3 to avoid rate limiting/timeout issues)
        content_pieces = []
        for result in scored_results[:2]:
            url = result.get("url", "")
            logger.info(f"Extracting content from {url}")
            
            content = self.extract_content(url)
            if content:
                # Add metadata about the source
                content_pieces.append(f"Source: {result.get('title', 'Unknown')} ({url})\n\n{content}")
        
        # Combine content pieces
        if content_pieces:
            combined_content = "\n\n---\n\n".join(content_pieces)
            
            # Limit content length (avoid token limits in generation)
            max_length = 4000
            if len(combined_content) > max_length:
                logger.info(f"Truncating content from {len(combined_content)} to {max_length} characters")
                combined_content = combined_content[:max_length] + "..."
            
            return combined_content
        else:
            logger.warning("Failed to extract any content from search results")
            return "" 