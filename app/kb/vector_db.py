"""
Vector Database module for the Math Agent
"""
import logging
from typing import List, Dict, Any, Optional, Tuple
import os
import numpy as np
from qdrant_client import QdrantClient
from qdrant_client.http import models
from qdrant_client.http.exceptions import UnexpectedResponse
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

class VectorDB:
    """
    Vector Database connector to handle knowledge base operations
    """
    
    def __init__(self, url: str = "localhost", port: int = 6333, 
                 collection_name: str = "math_knowledge_base"):
        """
        Initialize the Vector Database connection
        
        Args:
            url: URL of the Qdrant server
            port: Port of the Qdrant server
            collection_name: Name of the collection to use
        """
        self.url = url
        self.port = port
        self.collection_name = collection_name
        
        # Initialize embedding model
        try:
            # Using sentence-transformers for generating embeddings
            self.embedding_model = SentenceTransformer('all-MiniLM-L12-v2')
            self.vector_size = self.embedding_model.get_sentence_embedding_dimension()
            logger.info(f"Initialized embedding model with dimension: {self.vector_size}")
        except Exception as e:
            logger.error(f"Failed to initialize embedding model: {str(e)}")
            raise
        
        # Initialize Qdrant client
        try:
            self.client = QdrantClient(url=url, port=port)
            logger.info(f"Connected to Qdrant at {url}:{port}")
            
            # Check if collection exists, create if not
            try:
                self.client.get_collection(collection_name)
                logger.info(f"Collection '{collection_name}' exists")
            except UnexpectedResponse:
                # Create collection
                self.client.create_collection(
                    collection_name=collection_name,
                    vectors_config=models.VectorParams(
                        size=self.vector_size,
                        distance=models.Distance.COSINE
                    )
                )
                logger.info(f"Created collection '{collection_name}'")
        except Exception as e:
            logger.error(f"Failed to initialize Qdrant client: {str(e)}")
            raise
    
    def generate_embedding(self, text: str) -> List[float]:
        """
        Generate an embedding vector for the given text
        
        Args:
            text: The text to embed
            
        Returns:
            List[float]: The embedding vector
        """
        try:
            embedding = self.embedding_model.encode(text)
            return embedding.tolist()
        except Exception as e:
            logger.error(f"Error generating embedding: {str(e)}")
            raise
    
    def add_to_kb(self, text: str, metadata: Dict[str, Any]) -> str:
        """
        Add a text and its metadata to the knowledge base
        
        Args:
            text: The text to add
            metadata: Additional metadata about the text
            
        Returns:
            str: The ID of the added item
        """
        try:
            # Generate embedding
            embedding = self.generate_embedding(text)
            
            # Add text to metadata
            metadata["text"] = text
            
            # Generate a unique ID
            import uuid
            point_id = str(uuid.uuid4())
            
            # Add to Qdrant
            self.client.upsert(
                collection_name=self.collection_name,
                points=[
                    models.PointStruct(
                        id=point_id,
                        vector=embedding,
                        payload=metadata
                    )
                ]
            )
            
            logger.info(f"Added text to KB with ID: {point_id}")
            return point_id
        except Exception as e:
            logger.error(f"Error adding to KB: {str(e)}")
            raise
    
    def search(self, query: str, limit: int = 5, threshold: float = 0.7) -> Tuple[List[Dict[str, Any]], bool]:
        """
        Search the knowledge base for similar content
        
        Args:
            query: The search query
            limit: Maximum number of results to return
            threshold: Similarity threshold (0-1)
            
        Returns:
            Tuple[List[Dict], bool]: List of matching documents and a boolean indicating
                                    if any good matches were found
        """
        try:
            # Generate query embedding
            query_embedding = self.generate_embedding(query)
            
            # Search in Qdrant
            search_result = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_embedding,
                limit=limit
            )
            
            # Process results
            results = []
            found_good_match = False
            
            for scored_point in search_result:
                score = scored_point.score
                if score > threshold:
                    found_good_match = True
                
                # Extract payload and add score
                point_data = scored_point.payload
                point_data["score"] = score
                results.append(point_data)
            
            logger.info(f"Found {len(results)} results for query, good match: {found_good_match}")
            return results, found_good_match
        except Exception as e:
            logger.error(f"Error searching KB: {str(e)}")
            # Return empty results on error
            return [], False 