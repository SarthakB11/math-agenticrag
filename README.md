# Math Agent with Human-in-the-Loop Feedback

A virtual math professor that provides step-by-step solutions to mathematical problems using an Agentic RAG (Retrieval-Augmented Generation) architecture, with human feedback for continuous improvement.

---

## 🚀 Features

- **AI Gateway with Guardrails:** Ensures all interactions are focused on mathematics, maintaining safety and privacy.
- **Knowledge Base Integration:** Uses a vector database (Qdrant) to store and retrieve mathematical knowledge.
- **Web Search Capability:** Falls back to web search when the knowledge base lacks information.
- **Step-by-Step Solution Generation:** Provides clear, easy-to-understand solution steps.
- **Human-in-the-Loop Feedback:** Learns from user feedback to improve future responses.
- **Interactive Web Interface:** Simple, user-friendly interface using Streamlit.

---

## 🧰 Tech Stack

- **Backend:** Python (LangGraph, LangChain)
- **Frontend:** Streamlit
- **Vector Database:** Qdrant
- **LLM:** Google AI (Gemini-Pro)
- **Search API:** Tavily/Serper
- **Embedding:** Sentence Transformers
- **HITL Framework:** DSPy-ai
- **Other:** FastAPI, MongoDB (via pymongo), dotenv

---

## 🛠️ Architecture

The system uses an Agentic RAG architecture with the following components:

1. **AI Gateway:** Entry/exit point, enforcing guardrails.
2. **Routing Agent:** Directs queries to either the knowledge base or web search.
3. **Knowledge Base:** Vector database (Qdrant) storing math knowledge.
4. **Web Search Agent:** Performs targeted web searches and extracts content.
5. **Generation Agent:** Synthesizes information into step-by-step solutions.
6. **Human Feedback Loop:** Collects and integrates user feedback.

---

## 📁 Project Structure

```
math-homework-helper/
├── app.py                  # Main Streamlit app entry point
├── requirements.txt        # Python dependencies
├── env.sample              # Example environment variables
├── .env                    # (Not committed) Your actual environment variables
├── app/                    # Core application modules (agents, kb, feedback, etc.)
├── scripts/
│   ├── init_db.py          # Script to initialize the vector DB
│   └── load_knowledge_base.py # Script to load sample data
├── .github/workflows/
│   └── deploy.yml          # GitHub Actions workflow for deployment
└── ...
```

---

## 🔧 Installation & Local Development

### Prerequisites

- Python 3.8+
- pip
- Docker (for Qdrant)
- Git

### Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/your-username/math-homework-helper.git
   cd math-homework-helper
   ```

2. **Set up a Python virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

4. **Configure environment variables:**
   ```bash
   cp env.sample .env
   ```
   Edit `.env` with your API keys and configuration.

5. **Start Qdrant (Vector Database) using Docker:**
   ```bash
   docker run -p 6333:6333 -p 6334:6334 qdrant/qdrant
   ```

6. **Initialize the database:**
   ```bash
   python scripts/init_db.py
   ```

7. **Load sample data into the knowledge base:**
   ```bash
   python scripts/load_knowledge_base.py
   ```

8. **Run the Streamlit app:**
   ```bash
   streamlit run app.py
   ```

---

## 🚀 Deployment (GitHub Actions)

A ready-to-use GitHub Actions workflow is provided at `.github/workflows/deploy.yml`. On push to `main`, it will:

- Set up Python and dependencies
- Start Qdrant in Docker
- Run your Streamlit app

To use Qdrant Cloud, set VECTOR_DB_URL and VECTOR_DB_API_KEY in your .env or as GitHub Actions secrets.

### Required Secrets

Set these secrets in your GitHub repository (Settings → Secrets and variables → Actions):

- `LLM_API_KEY`
- `SEARCH_API_KEY`
- `VECTOR_DB_URL`
- `VECTOR_DB_PORT`
- `VECTOR_DB_COLLECTION`
- `DB_CONNECTION_STRING`
- `DEBUG`
- `LOG_LEVEL`

(Reference your `.env.sample` for any additional secrets your app may require.)

---

## 📝 Environment Variables

See `env.sample` for all required environment variables:

- `LLM_API_KEY`
- `VECTOR_DB_URL`
- `VECTOR_DB_PORT`
- `VECTOR_DB_COLLECTION`
- `SEARCH_API_KEY`
- `DB_CONNECTION_STRING`
- `DEBUG`
- `LOG_LEVEL`

---

## 🧪 Testing

To run tests:
```bash
pytest
```

## 📁 Project Structure

```
maths-homework-helper/
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
- Powered by Google AI's Gemini models

