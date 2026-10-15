# 🐍 PyChamp

<p align="center">
  <strong>An AI-powered Data Structures & Algorithms learning platform and integrated browser Python IDE.</strong>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.12+-3776AB?style=flat&logo=python&logoColor=white" alt="Python 3.12+">
  <img src="https://img.shields.io/badge/Django-5.x-092E20?style=flat&logo=django&logoColor=white" alt="Django">
  <img src="https://img.shields.io/badge/LangGraph-Multi--Agent-FF6F00?style=flat" alt="LangGraph">
  <img src="https://img.shields.io/badge/LangChain-LLM_Orchestration-1C3C3C?style=flat" alt="LangChain">
  <img src="https://img.shields.io/badge/Groq-Fast_Inference-F05A28?style=flat" alt="Groq">
  <img src="https://img.shields.io/badge/License-Educational-blue.svg?style=flat" alt="License">
</p>

---

## 📌 Overview

**PyChamp** bridges the gap between conceptual understanding and practical coding for Data Structures & Algorithms (DSA). By pairing a **concurrent multi-agent AI tutor** (powered by LangGraph and Groq) with an **instant in-browser Python code execution environment**, PyChamp delivers an interactive and guided learning journey from intuition to implementation.

---

## ✨ Key Features

### 🧠 1. AI DSA Tutor (Multi-Agent LangGraph Engine)
Submit any algorithmic concept (e.g., *"Merge Sort"*, *"LRU Cache"*, *"Dijkstra's Algorithm"*, *"Two Sum"*), and PyChamp spins up **three parallel AI specialist agents** orchestrated via LangGraph:

| Specialist Agent | Responsibility | LLM Powered By |
| :--- | :--- | :--- |
| **📖 Theory Agent** | Conceptual foundation, intuitive real-world analogies, step-by-step mechanics, and asymptotic analysis (Time & Space). Purely theoretical. | `openai/gpt-oss-20b` *(via Groq)* |
| **📝 Pseudocode Agent** | Clean, structured, language-agnostic logic and algorithmic blueprint. | `qwen/qwen3.8-27b` *(via Groq)* |
| **🐍 Code Agent** | Idiomatic, production-ready Python solution with modular helper functions, line-by-line explanations, and complexity summary. | `openai/gpt-oss-120b` *(via Groq)* |

#### 🎯 Guided Progressive Unlock Mechanism
Rather than overwhelming learners with all material at once, the DSA web portal implements a structured pedagogical flow:
1. **Theory First:** Students study theoretical foundations and algorithmic principles.
2. **Pseudocode Unlock:** Acknowledging the theory unlocks the high-level pseudocode tab.
3. **Python Implementation:** Acknowledging the pseudocode unlocks the full Python code implementation and detailed breakdown.
4. **Rich Markdown Rendering:** Formatted in real-time with `Marked.js` including syntax highlighting and structured tables.

---

### 💻 2. In-Browser Python IDE
A lightweight, modern dark-themed code editor engineered for rapid experimentation:

- **Monospace Editor:** Clean typography, line numbering support, and custom scrollbars.
- **One-Click & Hotkey Execution:** Run code instantly using the UI button or <kbd>Ctrl</kbd> + <kbd>Enter</kbd>.
- **Real-Time Output & Error Stream:** Distinct panels for standard output (`stdout`) and detailed traceback errors (`stderr`).
- **Execution Safeguards:** Server-side execution isolated through temporary script files with a **5-second timeout guard** against infinite loops.
- **Seamless Navigation:** Instantly switch between the Code Editor (`/`) and the DSA Tutor (`/dsa/`).

---

### 📓 3. Standalone Prototyping Pipeline (`PyChamp.ipynb`)
Includes an interactive Jupyter notebook replicating the complete LangGraph multi-agent pipeline for testing, prompt tuning, and independent experimentation.

---

## ⚙️ Architecture & Multi-Agent Flow

```
                     ┌────────────────────────┐
                     │   User DSA Topic Input │
                     │   (e.g., "Merge Sort") │
                     └───────────┬────────────┘
                                 │
                                 ▼
                     ┌────────────────────────┐
                     │   LangGraph Pipeline   │
                     │       START Node       │
                     └───────────┬────────────┘
                                 │
         ┌───────────────────────┼───────────────────────┐
         │ (Parallel Branch)     │ (Parallel Branch)     │ (Parallel Branch)
         ▼                       ▼                       ▼
 ┌───────────────┐       ┌───────────────┐       ┌───────────────┐
 │ Theory Agent  │       │ Pseudocode    │       │ Code Agent    │
 │ (gpt-oss-20b) │       │ (qwen3.8-27b) │       │(gpt-oss-120b) │
 └───────┬───────┘       └───────┬───────┘       └───────┬───────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 ▼
                     ┌────────────────────────┐
                     │   LangGraph END Node   │
                     │ (State Synchronization)│
                     └───────────┬────────────┘
                                 │
                                 ▼
                     ┌────────────────────────┐
                     │ JSON Response Payload  │
                     │  (Theory, Pseudo, Code)│
                     └────────────────────────┘
```

---

## 🏗️ Project Structure

```
Py-Champ/
├── .env.example                # Sample environment configuration template
├── .gitignore                  # Git ignore rules for Python, Django, IDEs & OS
├── PyChamp.ipynb               # Standalone Jupyter notebook with LangGraph pipeline
├── requirements.txt            # Project dependencies
├── pychamp/                    # Django application root
│   ├── manage.py               # Django CLI management script
│   ├── .env.example            # App-level env template
│   ├── .gitignore              # Repository git ignore configuration
│   ├── db.sqlite3              # Local SQLite database
│   ├── pychamp/                # Project configuration package
│   │   ├── __init__.py
│   │   ├── asgi.py             # ASGI configuration
│   │   ├── settings.py         # Django settings & static configuration
│   │   ├── urls.py             # Top-level URL routing (/ and /dsa/)
│   │   └── wsgi.py             # WSGI configuration
│   ├── pyeditor/               # Core application
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── dsa_agent.py        # LangGraph StateGraph agent definitions & prompts
│   │   ├── dsa_views.py        # DSA view controller & /dsa/invoke/ endpoint
│   │   ├── models.py
│   │   ├── views.py            # Code editor controller & /run_code/ execution logic
│   │   ├── migrations/         # Database migrations
│   │   │   └── __init__.py
│   │   ├── static/editor/      # Static assets
│   │   │   ├── dsa.css         # Modern styling for DSA learning interface
│   │   │   ├── editor.css      # Dark-themed IDE stylesheet
│   │   │   └── logo.png        # PyChamp branding logo
│   │   └── templates/          # HTML templates
│   │       ├── dsa.html        # Interactive multi-tab progressive DSA page
│   │       └── editor.html     # Split-screen code editor & output console
│   └── static/                 # Collected static directory placeholder
└── venv/                       # Python virtual environment (ignored by Git)
```

---

## 🚀 Getting Started

### Prerequisites

- **Python 3.12+**
- **Git**
- A free **[Groq API Key](https://console.groq.com/)** to power the high-speed LLM inference.

---

### 1. Clone the Repository

```bash
git clone https://github.com/SohamMistry01/PyChamp.git
cd Py-Champ
```

---

### 2. Set Up a Virtual Environment

**Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**macOS / Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

---

### 3. Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

---

### 4. Configure Environment Variables

Create a `.env` file in the project root:

```bash
cp .env.example .env
```

Open `.env` and insert your Groq API key:

```env
GROQ_API_KEY="gsk_your_actual_groq_api_key_here"
```

> **Note:** `dsa_agent.py` automatically looks up the directory tree to load the `.env` file from the project root.

---

### 5. Apply Migrations & Launch Server

Navigate into the Django project directory:

```bash
cd pychamp
python manage.py migrate
python manage.py runserver
```

Once running, access the application in your browser:

| Interface | URL | Description |
| :--- | :--- | :--- |
| **Python Code Editor** | [http://127.0.0.1:8000/](http://127.0.0.1:8000/) | Live browser IDE with code execution |
| **DSA AI Tutor** | [http://127.0.0.1:8000/dsa/](http://127.0.0.1:8000/dsa/) | Guided AI lesson with progressive unlocks |

---

### 6. (Optional) Run the Standalone Notebook

If you prefer to experiment with the LangGraph pipeline directly:

```bash
# From workspace root
jupyter notebook PyChamp.ipynb
```

Invoke the compiled graph directly in Python:

```python
from pyeditor.dsa_agent import invoke_dsa_agent

response = invoke_dsa_agent("Quick Sort")
print(response["theory"])
print(response["pseudocode"])
print(response["code"])
```

---

## 🔌 API Reference

### 1. Code Execution Endpoint

- **Route:** `POST /run_code/`
- **Content-Type:** `application/x-www-form-urlencoded`

**Request Payload:**
```
code=def add(a, b): return a + b\nprint(add(5, 7))
```

**Response (`200 OK`):**
```json
{
  "output": "12\n",
  "error": ""
}
```

---

### 2. DSA Tutor Agent Invocation

- **Route:** `POST /dsa/invoke/`
- **Content-Type:** `application/json` or `application/x-www-form-urlencoded`

**Request Payload (JSON):**
```json
{
  "topic": "Binary Search"
}
```

**Response (`200 OK`):**
```json
{
  "topic": "Binary Search",
  "theory": "### Binary Search\n\nBinary Search is an efficient algorithm...",
  "pseudocode": "```text\nfunction binarySearch(arr, target):\n    low = 0\n    high = length(arr) - 1\n    ...",
  "code": "```python\ndef binary_search(arr, target):\n    # Implementation\n..."
}
```

---

## 🛠️ Tech Stack

| Category | Technology |
| :--- | :--- |
| **Backend Framework** | Django 5.x (Python) |
| **AI Multi-Agent Framework** | LangGraph & LangChain |
| **LLM Inference Engine** | Groq Cloud API |
| **Models Utilized** | `openai/gpt-oss-20b`, `qwen/qwen3.8-27b`, `openai/gpt-oss-120b` |
| **Frontend** | HTML5, Vanilla CSS3 (Custom Dark Theme), Vanilla JavaScript |
| **Markdown Parser** | [Marked.js](https://marked.js.org/) (CDN) |
| **Environment Config** | `python-dotenv` |

---

## 🛡️ Security Considerations

> [!IMPORTANT]
> - **Server-Side Code Execution:** The code editor executes user-submitted Python code server-side using Python's `subprocess` module.
> - **Timeout Guard:** A strict **5-second timeout** is enforced on all code execution to prevent infinite loops and resource hogging.
> - **Production Deployment:** For public-facing deployments, code execution must be isolated inside a secure sandbox container (e.g., Docker container, gVisor, or AWS Lambda) with restricted filesystem and network access.
> - **API Key Safety:** Never check in your `.env` file to version control. The `.gitignore` is configured to prevent committing secrets.

---

## 🤝 Contributing

Contributions, issues, and feature requests are welcome!

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m "Add some AmazingFeature"`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📄 License

Distributed under the MIT License. See `LICENSE` for more information (Educational project).
