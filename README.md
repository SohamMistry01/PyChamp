# 🐍 PyChamp

<p align="center">
  <strong>An AI-powered Data Structures & Algorithms learning platform and integrated browser Python IDE.</strong>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.12+-3776AB?style=flat&logo=python&logoColor=white" alt="Python 3.12+">
  <img src="https://img.shields.io/badge/Django-5.2+-092E20?style=flat&logo=django&logoColor=white" alt="Django">
  <img src="https://img.shields.io/badge/LangGraph-Multi--Agent-FF6F00?style=flat" alt="LangGraph">
  <img src="https://img.shields.io/badge/LangChain-LLM_Orchestration-1C3C3C?style=flat" alt="LangChain">
  <img src="https://img.shields.io/badge/Groq-Fast_Inference-F05A28?style=flat" alt="Groq">
  <img src="https://img.shields.io/badge/Marked.js-Markdown_Engine-black?style=flat&logo=markdown" alt="Marked.js">
  <img src="https://img.shields.io/badge/Tests-23_Passing-brightgreen?style=flat" alt="Tests">
  <img src="https://img.shields.io/badge/License-MIT-blue.svg?style=flat" alt="License">
</p>

---

## 📌 Overview

**PyChamp** is a modern developer ecosystem designed to accelerate Python mastery and algorithmic problem-solving. By pairing a **concurrent multi-agent AI tutor** (orchestrated with LangGraph and powered by Groq's high-speed inference) with an **isolated in-browser Python code execution environment** and an **offline personal study library**, PyChamp delivers a complete pedagogical pipeline from intuition to implementation.

Whether you are executing Python scripts in real time, breaking down complex algorithms step-by-step, or reviewing saved notes with zero token overhead, PyChamp provides a focused, cohesive workspace tailored to every stage of your coding journey.

---

## ✨ Key Modules & Features

### 🧠 1. AI DSA Tutor (Multi-Agent LangGraph Engine)
Submit any algorithmic problem or computer science topic (e.g., *"Merge Sort"*, *"LRU Cache"*, *"Dijkstra's Algorithm"*, *"Two Sum"*, *"Binary Search Trees"*), and PyChamp launches **three parallel AI specialist agents** orchestrated via LangGraph:

| Specialist Agent | Responsibility | LLM Powered By | Temperature |
| :--- | :--- | :--- | :--- |
| **📖 Theory Agent** | Conceptual foundation, intuitive real-world analogies, step-by-step mechanics, and asymptotic analysis (Time & Space). Purely theoretical with no spoiler code. | `openai/gpt-oss-20b` *(via Groq)* | `0.2` |
| **📝 Pseudocode Agent** | Clean, structured, language-agnostic logic and algorithmic blueprint. | `qwen/qwen3.8-27b` *(via Groq)* | `0.2` |
| **🐍 Code Agent** | Idiomatic, production-ready Python solution with modular helper functions, line-by-line explanations, and complexity breakdown. | `openai/gpt-oss-120b` *(via Groq)* | `0.2` |

#### 🎯 Guided Progressive Pedagogical Flow
To encourage active recall and deep learning over passive reading, the tutor employs a guided step-by-step unlock flow:
1. **Theory First:** The student studies the foundational principles and asymptotic behavior.
2. **Pseudocode Unlock:** Acknowledging the theory (*"✓ I've studied this"*) unlocks the language-agnostic pseudocode blueprint.
3. **Python Implementation:** Acknowledging the pseudocode unlocks the full, executable Python code and line-by-line explanation.
4. **Markdown Rendering:** Formatted in real time using `Marked.js` with syntax highlighting and structured complexity tables.
5. **Real-Time Error Inspector:** Built-in error banner with expandable diagnostic drawers displaying stack traces, error types, and one-click log copying if an API error occurs.

---

### 💻 2. In-Browser Python IDE (`/editor/`)
A lightweight, modern dark-themed code editor engineered for rapid experimentation:

- **Monospace Editor:** Clean typography, line numbering support, and custom scrollbars.
- **One-Click & Hotkey Execution:** Run code instantly using the UI button or <kbd>Ctrl</kbd> + <kbd>Enter</kbd>.
- **Dual Console Stream:** Real-time terminal output with clear visual separation between standard output (`stdout`) and exception tracebacks (`stderr`).
- **Execution Guard:** Server-side execution isolated inside temporary files with a strict **5-second timeout safeguard** to prevent infinite loops and resource starvation.

---

### 📚 3. Local Study Notes Library (`/notes/`)
PyChamp allows users to archive generated lessons directly to their local disk with a single click:

- **Local Markdown Storage:** Lessons are saved into a dedicated folder under `saved_notes/<username>/<topic_slug>/` containing three separate markdown documents:
  - `theory.md`
  - `pseudocode.md`
  - `code.md`
- **Zero Token Overhead:** Review previously learned concepts offline at any time without consuming LLM API calls.
- **Interactive Library Viewer:**
  - Topic search & real-time filtering.
  - Collapsible accordion file tree.
  - In-place Markdown rendering for Theory, Pseudocode, and Code tabs.
  - One-click topic deletion and disk cleanup.

---

### 🔑 4. Multi-Tenant Groq API Key Management
PyChamp implements per-user API key isolation to ensure privacy and eliminate shared rate-limit bottlenecks:

- **User-Isolated Keys:** Each user configures their personal, free Groq API key in their profile or via the interactive onboarding modal.
- **Smart Modal Flow:** Users without an API key see clear setup indicators on the dashboard and can configure their key with step-by-step instructions in under 60 seconds without leaving the page.
- **Key Validation & Masking:** Validates the `gsk_` format, persists the key securely in `UserProfile`, and masks it (`gsk_...xxxx`) in administrative and client views.
- **Superuser Fallback:** Platform administrators can utilize their personal key or fall back to the environment-level `GROQ_API_KEY` defined in `.env`.

---

### 👤 5. User Profiles & Authentication
- **Dual Login Identifier:** Sign in using either username or email address.
- **Session Persistence:** Configurable "Remember Me" support (14-day persistent session vs. browser session).
- **Personalized Learning Profiles:** Track experience level (`Beginner`, `Intermediate`, `Advanced`), maintain personal bios and learning objectives.
- **Security Protections:** Password hashing via Django PBKDF2, input validation, and open-redirect defenses (`url_has_allowed_host_and_scheme`).

---

### 🛡️ 6. Branded Django Administration (`/admin/`)
- Custom-styled Django Admin with PyChamp branding and quick **"Back to PyChamp"** dashboard navigation link.
- Inlined `UserProfile` management displaying experience levels, custom Groq key status badges, and total saved topic counts.
- Searchable and filterable by staff status, superuser status, and experience level.

---

## ⚙️ Multi-Agent Architecture & Data Flow

```
                     ┌────────────────────────────────┐
                     │      User DSA Topic Input      │
                     │ (e.g., "Dijkstra's Algorithm") │
                     └───────────────┬────────────────┘
                                     │
                                     ▼
                     ┌────────────────────────────────┐
                     │    LangGraph Pipeline START    │
                     │    State: topic, api_key       │
                     └───────────────┬────────────────┘
                                     │
             ┌───────────────────────┼───────────────────────┐
             │ (Parallel Branch)     │ (Parallel Branch)     │ (Parallel Branch)
             ▼                       ▼                       ▼
     ┌───────────────┐       ┌───────────────┐       ┌───────────────┐
     │ Theory Agent  │       │ Pseudocode    │       │  Code Agent   │
     │               │       │     Agent     │       │               │
     │(gpt-oss-20b)  │       │ (qwen3.8-27b) │       │(gpt-oss-120b) │
     └───────┬───────┘       └───────┬───────┘       └───────┬───────┘
             │                       │                       │
             └───────────────────────┼───────────────────────┘
                                     │
                                     ▼
                     ┌────────────────────────────────┐
                     │     LangGraph Pipeline END     │
                     │    Synchronized State Merge    │
                     └───────────────┬────────────────┘
                                     │
                                     ▼
                     ┌────────────────────────────────┐
                     │     JSON Response Payload      │
                     │  - theory (Markdown)           │
                     │  - pseudocode (Markdown)       │
                     │  - code (Python + Markdown)    │
                     └───────────────┬────────────────┘
                                     │
                     ┌───────────────┴────────────────┐
                     ▼                                ▼
       ┌───────────────────────────┐    ┌───────────────────────────┐
       │   Progressive UI Tabs     │    │    Local Storage Disk     │
       │ (Theory -> Pseudo -> Code)│    │ saved_notes/<user>/<slug> │
       └───────────────────────────┘    └───────────────────────────┘
```

---

## 🏗️ Project Structure

```
pychamp/
├── manage.py                   # Django CLI management script
├── db.sqlite3                  # Local SQLite database
├── .env.example                # Sample environment configuration template
├── .gitignore                  # Git ignore rules for Python, Django, DB & media
├── README.md                   # Project documentation
│
├── saved_notes/                # User offline study library (created on demand)
│   └── <username>/             # Per-user isolated directory
│       └── <topic_slug>/       # Topic folder
│           ├── theory.md       # Conceptual explanation & complexity analysis
│           ├── pseudocode.md   # Algorithmic pseudocode
│           └── code.md         # Production Python implementation
│
├── pychamp/                    # Django project configuration package
│   ├── __init__.py
│   ├── asgi.py                 # ASGI configuration for async support
│   ├── settings.py             # Global settings, apps, auth, and static config
│   ├── urls.py                 # Top-level URL routing table
│   └── wsgi.py                 # WSGI configuration for production deployment
│
└── pyeditor/                   # Core PyChamp application
    ├── __init__.py
    ├── admin.py                # Admin site branding and UserProfile inline
    ├── apps.py                 # Pyeditor application config
    ├── dsa_agent.py            # LangGraph multi-agent StateGraph pipeline
    ├── dsa_views.py            # DSA generation, notes export & API key views
    ├── models.py               # UserProfile model & filesystem persistence logic
    ├── tests.py                # Comprehensive test suite (23 passing tests)
    ├── views.py                # Auth, dashboard, editor & code execution views
    │
    ├── static/editor/          # Stylesheets and visual assets
    │   ├── auth.css            # Styles for login, registration & profile forms
    │   ├── dsa.css             # DSA learning interface styles & animations
    │   ├── editor.css          # Dark-themed IDE stylesheet
    │   ├── home.css            # Home dashboard 2x2 modular grid layout
    │   ├── logo.png            # PyChamp official brand logo
    │   └── saved_notes.css     # Saved notes library tree & preview layout
    │
    └── templates/              # Semantic HTML templates
        ├── admin/
        │   └── base_site.html  # Branded admin template with "Back to PyChamp"
        ├── dsa.html            # Multi-tab progressive DSA AI tutor
        ├── editor.html         # Live Python editor & split output console
        ├── groq_modal.html     # Reusable Groq API key setup modal
        ├── home.html           # Home dashboard with status badge & module cards
        ├── login.html          # Clean sign-in page with username/email support
        ├── profile.html        # Profile management & experience settings
        ├── register.html       # User registration page
        └── saved_notes.html    # Interactive local study notes explorer
```

---

## 🚀 Getting Started

### Prerequisites

- **Python 3.12+**
- **Git**
- A free **[Groq Cloud API Key](https://console.groq.com/keys)** (free tier, zero token cost)

---

### 1. Clone the Repository

```bash
git clone https://github.com/SohamMistry01/PyChamp.git
cd PyChamp/pychamp
```

---

### 2. Set Up a Virtual Environment

**Windows (PowerShell):**
```powershell
python -m venv ..\venv
..\venv\Scripts\Activate.ps1
```

**macOS / Linux:**
```bash
python3 -m venv ../venv
source ../venv/bin/activate
```

---

### 3. Install Dependencies

Install the required packages from the project's root:

```bash
pip install --upgrade pip
pip install -r ../requirements.txt
```

#### Core Dependencies:
- `django` — Core web framework and ORM
- `langgraph` — Multi-agent state graph orchestration
- `langchain` & `langchain-groq` — LLM integration and prompt chaining
- `python-dotenv` — Environment variable management

---

### 4. Configure Environment Variables

Create a `.env` file inside `pychamp/` (or the repository root):

```bash
cp .env.example .env
```

Open `.env` and set your fallback Groq API key:

```env
GROQ_API_KEY="gsk_your_actual_groq_api_key_here"
```

> **Note:** Regular users can also configure their own personal key dynamically inside the app UI via the profile page or onboarding modal.

---

### 5. Apply Migrations & Create Superuser

Initialize the SQLite database schema:

```bash
python manage.py migrate
```

Create an administrator account to access the Django Admin Portal:

```bash
python manage.py createsuperuser
```

---

### 6. Launch the Development Server

Start the Django development server:

```bash
python manage.py runserver
```

Open your browser and navigate to:
- **PyChamp Portal:** [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
- **Django Admin:** [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/)

---

## 🧪 Running the Test Suite

PyChamp includes a thorough automated test suite covering models, authentication, security boundaries, multi-agent key resolution, file I/O operations, and view templates.

To run the complete test suite:

```bash
python manage.py test
```

Expected output:
```text
Found 23 test(s).
Creating test database for alias 'default'...
.......................
----------------------------------------------------------------------
Ran 23 tests in ~25s

OK
Destroying test database for alias 'default'...
```

---

## 🔌 URL Routing & API Reference

### Application Routes

| Path | View Function | Method | Description | Access |
| :--- | :--- | :--- | :--- | :--- |
| `/` | `home_view` | `GET` | Main dashboard with 2x2 modular navigation & agent status | Authenticated |
| `/editor/` | `editor_view` | `GET` | In-browser Python IDE | Authenticated |
| `/dsa/` | `dsa_view` | `GET` | Progressive DSA AI tutor interface | Authenticated |
| `/notes/` | `saved_notes_view` | `GET` | Saved DSA notes browser & markdown previewer | Authenticated |
| `/profile/` | `profile_view` | `GET`, `POST` | User profile settings, experience level & Groq key | Authenticated |
| `/login/` | `login_view` | `GET`, `POST` | User login (username or email) | Public |
| `/register/` | `register_view` | `GET`, `POST` | Account creation & initial profile setup | Public |
| `/logout/` | `logout_view` | `GET` | Terminate session and redirect to login | Authenticated |
| `/admin/` | `admin.site.urls` | `GET`, `POST` | Branded Django administration console | Staff / Superuser |

---

### API Endpoints

#### 1. Python Code Execution
- **Endpoint:** `POST /run_code/`
- **Content-Type:** `application/x-www-form-urlencoded`
- **Payload:** `code=<python_code_string>`
- **Response:**
  ```json
  {
    "output": "Hello, PyChamp!\n",
    "error": ""
  }
  ```

#### 2. DSA Multi-Agent Invocation
- **Endpoint:** `POST /dsa/invoke/`
- **Content-Type:** `application/json` or `application/x-www-form-urlencoded`
- **Payload:**
  ```json
  {
    "topic": "Binary Search"
  }
  ```
- **Response (`200 OK`):**
  ```json
  {
    "topic": "Binary Search",
    "theory": "### Binary Search\n\nBinary Search is an efficient algorithm...",
    "pseudocode": "```text\nfunction binarySearch(arr, target):\n...",
    "code": "```python\ndef binary_search(arr, target):\n..."
  }
  ```
- **Error Response (`403 Forbidden` - Missing User Key):**
  ```json
  {
    "error": "Personal Groq API key required...",
    "error_type": "ApiKeyRequiredError",
    "needs_key": true,
    "topic": "Binary Search"
  }
  ```

#### 3. Save DSA Notes to Local Disk
- **Endpoint:** `POST /dsa/save/`
- **Payload (JSON):**
  ```json
  {
    "topic": "Selection Sort",
    "theory": "# Theory...",
    "pseudocode": "# Pseudocode...",
    "code": "# Python Code..."
  }
  ```
- **Response (`200 OK`):**
  ```json
  {
    "success": true,
    "message": "Successfully saved 'Selection Sort' notes to local machine directory!",
    "note": {
      "topic": "Selection Sort",
      "folder_name": "selection_sort",
      "relative_path": "saved_notes/alex/selection_sort",
      "saved_at": "Oct 17, 2026 • 09:30 PM",
      "files": {
        "theory": "theory.md",
        "pseudocode": "pseudocode.md",
        "code": "code.md"
      }
    },
    "total_saved": 4
  }
  ```

#### 4. Save Personal Groq API Key
- **Endpoint:** `POST /dsa/save_api_key/`
- **Payload (JSON):**
  ```json
  {
    "api_key": "gsk_your_groq_api_key_here"
  }
  ```
- **Response (`200 OK`):**
  ```json
  {
    "success": true,
    "message": "Groq API key saved successfully! Your AI DSA Tutor is now unlocked.",
    "masked_key": "gsk_...9a12"
  }
  ```

#### 5. Fetch Saved Note Content
- **Endpoint:** `GET /notes/content/?folder=binary_search&type=theory`
- **Response (`200 OK`):**
  ```json
  {
    "success": true,
    "folder_name": "binary_search",
    "topic": "Binary Search",
    "file_type": "theory",
    "content": "### Binary Search\n...",
    "filename": "theory.md"
  }
  ```

#### 6. Delete Saved Note
- **Endpoint:** `POST /notes/delete/`
- **Payload (JSON):**
  ```json
  {
    "folder_name": "binary_search"
  }
  ```
- **Response (`200 OK`):**
  ```json
  {
    "success": true,
    "message": "Successfully deleted 'binary_search' notes.",
    "folder_name": "binary_search",
    "total_saved": 3
  }
  ```

---

## 🛡️ Security & Architecture Best Practices

> [!IMPORTANT]
> - **Subprocess Isolation & Timeout:** Code submitted in the in-browser IDE is executed in an isolated Python subprocess with a strict **5-second timeout guard** (`subprocess.TimeoutExpired`).
> - **Path Sanitization:** Folder and file names generated during note-saving operations are sanitized using regex (`sanitize_folder_name`), mitigating path traversal risks.
> - **Open Redirect Prevention:** All authentication redirect URLs are validated against `url_has_allowed_host_and_scheme` to prevent external phishing redirects.
> - **API Key Safety:** Custom API keys are bound to individual user accounts. Environment secrets in `.env` are strictly excluded from version control via `.gitignore`.
> - **Production Deployment:** For multi-user public environments, in-browser code execution should be containerized using a secure sandbox engine (e.g., Docker, nsjail, or AWS Lambda).

---

## 🛠️ Technology Stack Summary

| Layer | Technology |
| :--- | :--- |
| **Backend Framework** | Django 5.2+ (Python) |
| **Database** | SQLite3 (Configurable to PostgreSQL) |
| **AI Multi-Agent System** | LangGraph & LangChain |
| **Inference Engine** | Groq Cloud API |
| **Models Utilized** | `openai/gpt-oss-20b`, `qwen/qwen3.8-27b`, `openai/gpt-oss-120b` |
| **Frontend Architecture** | Semantic HTML5, Custom Vanilla CSS3 (Dark Theme), Vanilla JavaScript |
| **Markdown Engine** | [Marked.js](https://marked.js.org/) (CDN) |
| **Testing** | Django Test Framework (`django.test.TestCase`) |
| **Environment Config** | `python-dotenv` |

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository.
2. Create your feature branch (`git checkout -b feature/MyNewFeature`).
3. Commit your changes (`git commit -m "Add MyNewFeature"`).
4. Run tests to ensure everything passes (`python manage.py test`).
5. Push to your branch (`git push origin feature/MyNewFeature`).
6. Submit a Pull Request.

---

## 📄 License

Distributed under the **MIT License**. See `LICENSE` for details.
