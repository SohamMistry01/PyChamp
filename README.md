# 🐍 PyChamp

**PyChamp** is an AI-powered Data Structures & Algorithms learning platform with an integrated online Python code editor. It combines the intelligence of LLMs (via LangChain & LangGraph) with a Django-based web interface where learners can write and execute Python code directly in the browser.

---

## ✨ Features

### 🤖 AI DSA Tutor (LangGraph Pipeline)

Given any DSA topic (e.g. *"Selection Sort"*), PyChamp spins up **three parallel AI agents** that each produce a different learning artifact:

| Agent | What It Generates | LLM Used |
|-------|-------------------|----------|
| **Theory** | Detailed theoretical explanation — intuition, algorithm steps, complexity analysis | `openai/gpt-oss-20b` |
| **Pseudocode** | Clean, language-agnostic pseudocode | `meta-llama/llama-4-maverick-17b-128e-instruct` |
| **Code** | Production-quality Python implementation with step-by-step explanation & complexity breakdown | `openai/gpt-oss-120b` |

All three agents run **concurrently** via a LangGraph `StateGraph` and converge at the end, delivering a complete learning package in one invocation.

### 🖥️ Online Python Code Editor (Django Web App)

A browser-based Python editor where users can:

- **Write** Python code in a dark-themed, monospace editor
- **Run** code with a single click — executed server-side via `subprocess`
- **View** stdout output and stderr errors in real time

---

## 🏗️ Project Structure

```
Py-Champ/
├── .env                        # Environment variables (GROQ_API_KEY)
├── PyChamp.ipynb               # Jupyter notebook — AI DSA tutor pipeline
├── requirements.txt            # Python dependencies
├── pychamp/                    # Django project root
│   ├── manage.py               # Django management script
│   ├── db.sqlite3              # SQLite database
│   ├── pychamp/                # Django project settings
│   │   ├── settings.py         # Project configuration
│   │   ├── urls.py             # URL routing
│   │   ├── wsgi.py             # WSGI entry point
│   │   └── asgi.py             # ASGI entry point
│   └── pyeditor/               # Django app — code editor
│       ├── views.py            # Editor view & code execution endpoint
│       ├── templates/
│       │   └── editor.html     # Editor UI template
│       └── static/editor/
│           ├── editor.css      # Dark-themed editor styles
│           └── logo.png        # PyChamp logo
└── venv/                       # Python virtual environment
```

---

## 🚀 Getting Started

### Prerequisites

- Python 3.12+
- A [Groq API key](https://console.groq.com/) for the AI tutor

### 1. Clone & Set Up the Environment

```bash
git clone <repo-url>
cd Py-Champ

python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

pip install -r requirements.txt
```

### 2. Configure Environment Variables

Create a `.env` file in the project root:

```env
GROQ_API_KEY=your_groq_api_key_here
```

### 3. Run the AI DSA Tutor

Open `PyChamp.ipynb` in Jupyter Notebook or VS Code and run all cells. Invoke the graph with any DSA topic:

```python
result = graph.invoke({"topic": "Selection Sort"})
```

Access the results:

```python
from IPython.display import Markdown

Markdown(result['theory'])       # Detailed theory
Markdown(result['pseudocode'])   # Pseudocode
Markdown(result['code'])         # Python code + explanation
```

### 4. Run the Code Editor Web App

```bash
cd pychamp
python manage.py migrate
python manage.py runserver
```

Open [http://127.0.0.1:8000](http://127.0.0.1:8000) in your browser to access the editor.

---

## 🔧 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Renders the Python code editor UI |
| `POST` | `/run_code/` | Accepts Python code, executes it server-side, and returns JSON with `output` and `error` fields |

### Example `POST /run_code/`

**Request:**
```
Content-Type: application/x-www-form-urlencoded
code=print("Hello, World!")
```

**Response:**
```json
{
  "output": "Hello, World!\n",
  "error": ""
}
```

---

## ⚙️ How the AI Pipeline Works

PyChamp uses **LangGraph** to orchestrate a multi-agent workflow:

```
        ┌──────────┐
        │  START    │
        └────┬─────┘
             │
     ┌───────┼───────┐
     ▼       ▼       ▼
 ┌────────┐ ┌──────────┐ ┌──────┐
 │ Theory │ │Pseudocode│ │ Code │
 └───┬────┘ └────┬─────┘ └──┬───┘
     │           │           │
     └───────┬───────────────┘
             ▼
        ┌──────────┐
        │   END    │
        └──────────┘
```

1. The user provides a **topic** (e.g., *"Binary Search"*)
2. Three nodes run **in parallel**, each querying a different LLM via Groq
3. Results are merged into a single state dictionary with `theory`, `pseudocode`, and `code` keys

---

## 📦 Dependencies

| Package | Purpose |
|---------|---------|
| `django` | Web framework for the code editor |
| `langchain` | LLM orchestration framework |
| `langchain-groq` | Groq LLM provider integration |
| `langgraph` | Multi-agent graph execution |
| `python-dotenv` | Environment variable management |
| `ipykernel` | Jupyter notebook kernel |

---

## ⚠️ Security Notice

- The code editor executes arbitrary Python code on the server via `subprocess`. **Do not deploy this to a public server** without proper sandboxing.
- Code execution has a **5-second timeout** to prevent runaway processes.
- The `.env` file contains sensitive API keys — never commit it to version control.

---

## 📄 License

This project is for educational purposes.
