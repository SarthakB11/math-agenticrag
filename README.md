# Math Agent with Human-in-the-Loop Feedback

A virtual math professor that provides step-by-step solutions to mathematical problems using an Agentic RAG architecture with human feedback for continuous improvement.

## 🚀 Features

- **AI Gateway with Guardrails**: Ensures all interactions are focused on mathematics and maintains safety and privacy
- **Knowledge Base Integration**: Uses a Vector Database to store and retrieve mathematical knowledge
- **Web Search Capability**: Falls back to web search when the Knowledge Base lacks information
- **Step-by-Step Solution Generation**: Provides clear, easy-to-understand solution steps
- **Human-in-the-Loop Feedback**: Learns from user feedback to improve future responses
- **Interactive Web Interface**: Simple, user-friendly interface using Streamlit

## 🛠️ Architecture

The system uses an Agentic RAG architecture with the following components:

1. **AI Gateway**: Acts as the system's entry and exit point, enforcing guardrails
2. **Routing Agent**: Directs queries to either the Knowledge Base or Web Search
3. **Knowledge Base**: Vector Database storing math knowledge
4. **Web Search Agent**: Performs targeted web searches and extracts content
5. **Generation Agent**: Synthesizes information into step-by-step solutions
6. **Human Feedback Loop**: Collects and integrates user feedback

## 🧰 Tech Stack

- **Backend**: Python with LangGraph/LangChain
- **Frontend**: Streamlit
- **Vector Database**: Qdrant
- **LLM**: OpenAI (GPT-4)
- **Search API**: Tavily/Serper
- **Embedding**: Sentence Transformers
- **HITL Framework**: DSPy-ai

## 🔧 Installation

### Prerequisites

- Python 3.8+
- pip (Python package manager)
- Docker (optional, for Qdrant)

### Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/math-agenticrag.git
   cd math-agenticrag
   ```

2. Set up a Python virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables by copying the sample file:
   ```bash
   cp env.sample .env
   ```
   Then edit the `.env` file with your API keys and configuration.

5. Start Qdrant (Vector Database) using Docker:
   ```bash
   docker run -p 6333:6333 -p 6334:6334 qdrant/qdrant
   ```

6. Initialize the database:
   ```bash
   python scripts/init_db.py
   ```

7. Load sample data into the knowledge base:
   ```bash
   python scripts/load_knowledge_base.py
   ```

## 🚀 Running the Application

Start the Streamlit app:

```bash
streamlit run app.py
```

Visit the app at http://localhost:8501

## 📁 Project Structure

```
math-agenticrag/
├── app/                  # Core application code
│   ├── agents/           # Agent definitions and logic
│   │   ├── generation_agent.py  # LLM-based solution generation
│   │   └── routing_agent.py     # KB/Web routing logic
│   ├── gateway/          # AI Gateway implementation
│   │   └── ai_gateway.py        # Input/output validation
│   ├── kb/               # Knowledge Base integration
│   │   └── vector_db.py         # Vector database connector
│   ├── web_search/       # Web Search and extraction logic
│   │   └── search_agent.py      # Web search and content extraction
│   ├── feedback/         # Human-in-the-Loop feedback mechanism
│   │   └── feedback_loop.py     # Feedback collection and processing
│   └── models/           # Data models and schemas
│       └── database.py           # Database models
├── scripts/              # Utility scripts
│   ├── init_db.py                # Initialize database tables
│   └── load_knowledge_base.py    # Load sample data into KB
├── data/                 # Knowledge Base data and schemas
│   ├── kb_data/                  # Custom KB data files
│   └── feedback_logs/            # Feedback logs
├── Instructions/         # Project documentation
├── .env                  # Environment variables (not versioned)
├── env.sample            # Sample environment variables
├── requirements.txt      # Python dependencies
└── app.py                # Main application entry point
```

## 🔄 Workflow

1. User submits a math question through the UI
2. AI Gateway validates the input
3. Routing Agent checks the Knowledge Base for relevant information
4. If KB has good matches, the solution is generated from KB content
5. If KB lacks information, Web Search is performed to find solutions
6. Generation Agent creates a step-by-step solution
7. User sees the solution and can provide feedback (helpful/needs improvement)
8. Feedback is logged and used to improve future responses

## 🤝 Contributing

We welcome contributions! Please see the development workflow in the documentation folder.

## 📝 License

This project is licensed under the MIT License.

## 🙏 Acknowledgments

- Built using LangChain and LangGraph frameworks
- Uses Qdrant for vector storage
- Powered by OpenAI's models

