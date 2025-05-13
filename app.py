"""
Math Agent with Human-in-the-Loop Feedback
Main application entry point
"""
import os
import streamlit as st
from dotenv import load_dotenv
from app.agents.routing_agent import RoutingAgent
from app.agents.generation_agent import GenerationAgent
from app.kb.vector_db import VectorDB
from app.web_search.search_agent import WebSearchAgent
from app.gateway.ai_gateway import AIGateway
from app.feedback.feedback_loop import FeedbackLoop

# Load environment variables
load_dotenv()

# Initialize components
def init_components():
    """Initialize all components of the Math Agent system"""
    # Initialize Vector DB connection
    vector_db = VectorDB(
        url=os.getenv("VECTOR_DB_URL", "localhost"),
        port=int(os.getenv("VECTOR_DB_PORT", "6333")),
        collection_name=os.getenv("VECTOR_DB_COLLECTION", "math_knowledge_base")
    )
    
    # Initialize AI Gateway
    ai_gateway = AIGateway()
    
    # Initialize Web Search Agent
    web_search_agent = WebSearchAgent(
        api_key=os.getenv("SEARCH_API_KEY", "")
    )
    
    # Initialize Generation Agent
    generation_agent = GenerationAgent(
        api_key=os.getenv("LLM_API_KEY", "")
    )
    
    # Initialize Routing Agent
    routing_agent = RoutingAgent(
        vector_db=vector_db,
        web_search_agent=web_search_agent,
        generation_agent=generation_agent
    )
    
    # Initialize Feedback Loop
    feedback_loop = FeedbackLoop()
    
    return {
        "ai_gateway": ai_gateway,
        "routing_agent": routing_agent,
        "feedback_loop": feedback_loop
    }

# Streamlit UI
def main():
    st.set_page_config(
        page_title="Math Agent",
        page_icon="➗",
        layout="wide"
    )
    
    st.title("Math Agent 🧮")
    st.subheader("Your AI Math Professor")
    
    # Initialize components if not already in session state
    if "components" not in st.session_state:
        st.session_state.components = init_components()
        st.session_state.interaction_id = None
        st.session_state.solution = None
        st.session_state.source = None
    
    # User input
    with st.form(key="math_question_form"):
        question = st.text_area("Enter your math question:")
        submit_button = st.form_submit_button(label="Get Solution")
    
    # Process user question
    if submit_button and question:
        try:
            with st.spinner("Getting your solution..."):
                # Input guardrails check
                ai_gateway = st.session_state.components["ai_gateway"]
                if not ai_gateway.validate_input(question):
                    st.error("Please enter a valid math question.")
                    return
                
                # Route and generate solution
                routing_agent = st.session_state.components["routing_agent"]
                result = routing_agent.process(question)
                
                # Output guardrails check
                if not ai_gateway.validate_output(result["solution"]):
                    st.error("An issue occurred with the generated solution. Please try a different question.")
                    return
                
                # Store result in session state
                st.session_state.interaction_id = result["interaction_id"]
                st.session_state.solution = result["solution"]
                st.session_state.source = result["source"]
                
                # Display the solution
                st.success("Solution found!")
                
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
    
    # Display solution if available
    if st.session_state.solution:
        st.subheader("Step-by-step Solution")
        
        if isinstance(st.session_state.solution, list):
            for i, step in enumerate(st.session_state.solution, 1):
                st.markdown(f"**Step {i}:** {step}")
        else:
            st.markdown(st.session_state.solution)
            
        st.caption(f"Source: {'Knowledge Base' if st.session_state.source == 'knowledge_base' else 'Web Search'}")
        
        # Feedback section
        st.subheader("Was this solution helpful?")
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("👍 Yes, helpful!"):
                feedback_loop = st.session_state.components["feedback_loop"]
                feedback_loop.submit_feedback(
                    interaction_id=st.session_state.interaction_id,
                    feedback_type="helpful"
                )
                st.success("Thank you for your feedback!")
        
        with col2:
            if st.button("👎 No, needs improvement"):
                feedback_loop = st.session_state.components["feedback_loop"]
                feedback_loop.submit_feedback(
                    interaction_id=st.session_state.interaction_id,
                    feedback_type="needs_improvement"
                )
                st.success("Thank you for your feedback!")
        
        # Additional comments
        with st.expander("Leave additional comments"):
            feedback_text = st.text_area("Your comments:")
            if st.button("Submit Comments"):
                feedback_loop = st.session_state.components["feedback_loop"]
                feedback_loop.submit_detailed_feedback(
                    interaction_id=st.session_state.interaction_id,
                    feedback_text=feedback_text
                )
                st.success("Thank you for your detailed feedback!")

if __name__ == "__main__":
    main() 