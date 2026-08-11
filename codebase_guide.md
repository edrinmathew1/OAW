# 🎓 OAW (Observable Agent Runtime) — Complete Project & Lab Guide

This document explains every file in the codebase, how it satisfies the **7 core requirements** listed in `codebaserequirements.md`, and gives you a step-by-step script for explaining everything to your teacher.

---

## 🏛️ Project Summary & Domain
- **Project Name**: **OAW — Observable Agent Runtime**
- **Domain**: Artificial Intelligence and Agent Systems
- **Concept**: A transparent AI Agent system where an LLM (Qwen 2.5) executes tasks by selecting specialized tools with live execution observability.

---

## 🗺️ "Where is What" — File Map & Purpose

| File Name | Purpose & Contents | Lab Requirement Satisfied |
| :--- | :--- | :--- |
| **`main.py`** | Primary application entry point. Launches the Auth Dialog first, then opens the main PyQt6 window. | Requirements #2 & #3 |
| **`auth.py`** | Login and Registration System with PyQt6 dialogs, custom `ValidationError` exceptions, and user data storage. | **Requirement #2**: RegEx functions (`search`, `match`, `fullmatch`, `findall`, `split`, `compile`, `sub`) & Exception handling |
| **`cli.py`** | Full PyQt6 Desktop GUI with 4 layouts, 5 widgets, 5 signals/slots, 3 keyboard/mouse/close event overrides, and confirmation dialogs. | **Requirement #3**: PyQt6 GUI Application |
| **`tools/base.py`** | Abstract base class `AgentTool` with abstract method `execute()`, encapsulation, and registry array. | **Requirement #1**: OOP Concepts (Classes, Abstract Class/Method, Inheritance, Polymorphism, Encapsulation) |
| **`tools/search.py`** | Web search & Wikipedia REST API caller tool. Demonstrates dictionary functions (`.get()`, `.keys()`, `.values()`, `.items()`, `.update()`). | **Requirements #1 & #4**: Public API & Dictionary Functions |
| **`tools/file_tool.py`** | File Manager Tool for AI agent to perform document Q&A and text transformations. | **Requirements #1 & #7**: AI Tool & File Operations |
| **`tools/code.py`** | Code execution tool with `stdout` string capturing and inline math evaluation. | **Requirement #1**: Concrete Tool Subclass |
| **`tools/memory.py`** | Memory management tool using JSON file handling to remember user notes. | **Requirement #1**: Concrete Tool Subclass |
| **`tools/api_caller.py`** | REST API Caller tool for HTTP GET, POST, PUT, DELETE operations. | **Requirements #1 & #5**: REST API Tool |
| **`file_manager.py`** | User-defined functions for file CRUD (`w`, `r`, `a`, `r+`, `w+`), methods (`read`, `readline`, `readlines`, `write`, `writelines`, `seek`, `tell`, `close`), and RegEx checks. | **Requirement #7**: File Handling & RegEx Validation |
| **`file_demo.py`** | Standalone console demonstration script executing all file operations and printing pass/fail RegEx logs. | **Requirement #7**: Runnable File Demo |
| **`server.py`** | Flask REST API server exposing endpoints on port 5000 (`GET`, `POST` 201 Created, `PUT`, `DELETE`) with custom JSON error handlers (400, 404, 405, 500). | **Requirement #5**: Flask Web API & Error Handling |
| **`client_demo.py`** | Python client script using `requests` library to consume `server.py` REST API endpoints. | **Requirement #5**: API Client Script |
| **`app_streamlit.py`** | Web analytics and monitoring dashboard for OAW featuring Plotly charts, widgets, metrics, and file storage inspector. | **Requirement #6**: Streamlit Web Dashboard |
| **`agent/core.py` & `loop.py`** | Central agent controller, tool router, and ReAct loop passing observations back to Ollama. | **Requirement #1**: Agent Controller Module |

---

## 📑 Detailed Mapping to All 7 Requirements

### 1️⃣ Requirement #1: Object-Oriented Programming (OOP)
- **Base Class & Abstract Class**: `AgentTool` in `tools/base.py` uses `abc.ABC` and `@abstractmethod def execute(self, task: str) -> dict:`.
- **Inheritance**: Derived tool classes (`WebSearchTool`, `MemoryTool`, `CodeExecutionTool`, `APICallerTool`, `FileManagementTool`) inherit from `AgentTool`.
- **Polymorphism**: `AgentTool.registry` stores objects of different derived tool classes and invokes `tool.execute()` through a uniform interface.
- **Encapsulation**: Private attributes `_name`, `_description`, `_trigger_pattern` with property getters.

### 2️⃣ Requirement #2: Login & Registration System with RegEx & Exceptions
- Implemented in `auth.py`.
- **All 7 Python RegEx Functions Demonstrated**:
  1. `re.fullmatch()`: Validates Email address format (`validate_email`).
  2. `re.match()`: Validates Username starting letter (`validate_username`).
  3. `re.search()`: Validates Password complexity (digit & special char).
  4. `re.findall()`: Extracts digits from Phone number (`validate_phone`).
  5. `re.compile()`: Pre-compiled Developer Key regex object (`DEV-\d{4}`).
  6. `re.sub()`: Sanitizes extra whitespace in name/user strings.
  7. `re.split()`: Splits full name inputs by spaces/commas.
- **Exception Handling**: Custom `ValidationError` class and `try...except` handling with `QMessageBox` warning/error dialogs.

### 3️⃣ Requirement #3: PyQt6 GUI Application
- Implemented in `cli.py` and `auth.py`.
- **4 Layout Managers**: `QVBoxLayout`, `QHBoxLayout`, `QFormLayout`, `QSplitter`.
- **5 Widgets**: `QLineEdit`, `QTextEdit`, `QPushButton`, `QLabel`, `QSplitter` / `QMessageBox`.
- **5 Signals and Slots**:
  1. `input.returnPressed` -> `_on_send_click`
  2. `send_btn.clicked` -> `_on_send_click`
  3. `attach_btn.clicked` -> `_attach_file`
  4. `clear_btn.clicked` -> `_clear_chat`
  5. `worker.log_signal` / `result_signal` -> `_on_log` / `_on_result`
- **3 Event Handling Overrides**:
  1. `keyPressEvent(event)`: `Esc` cancels generation, `Ctrl+L` clears chat.
  2. `closeEvent(event)`: Confirmation dialog box ("Are you sure you want to exit?").
  3. `enterEvent(event)`: Window focus enter handling.

### 4️⃣ Requirement #4: Public API & Dictionary Functions
- Implemented in `tools/search.py`.
- Fetches real-time summaries from the **Wikipedia REST API** (`https://en.wikipedia.org/api/rest_v1/page/summary/...`).
- Demonstrates dictionary functions: `.get()`, `.keys()`, `.values()`, `.items()`, `.update()`.

### 5️⃣ Requirement #5: Flask REST API, JSON Dataset & Requests Client
- **Dataset**: `data/dataset.json` contains 10 structured JSON records for OAW Agent Tools.
- **Flask Server (`server.py`)**: Endpoints on `http://127.0.0.1:5000/api/records` with `GET`, `POST` (201 Created), `PUT`, `DELETE`.
- **Custom Errors**: Handlers for 400 Bad Request, 404 Not Found, 405 Method Not Allowed, 500 Internal Error.
- **Client Script (`client_demo.py`)**: Consumes server API using `requests` library.

### 6️⃣ Requirement #6: Streamlit Web Dashboard
- Implemented in `app_streamlit.py`.
- Serves as the web monitoring dashboard for OAW with Plotly bar/donut pie charts, sidebar widgets, and metrics.

### 7️⃣ Requirement #7: File Handling & RegEx Validation
- Implemented in `file_manager.py` and `file_demo.py`.
- **Modes**: `'w'`, `'r'`, `'a'`, `'r+'`, `'w+'`.
- **Methods**: `read()`, `readline()`, `readlines()`, `write()`, `writelines()`, `seek()`, `tell()`, `close()`.
- **User-Defined Functions**: `create_file()`, `read_all_records()`, `append_record()`, `search_record()`, `update_record()`, `delete_record()`, `create_backup()`.
- **RegEx Input Validation**: ID, Email, Date, Tool Code.

---

## 🗣️ Teacher Explanation Script & Presentation Guide

When presenting to your professor, follow this simple **5-Step Demo Script**:

### Step 1: Introduction (30 Seconds)
> *"Good morning professor! My project is **OAW — Observable Agent Runtime**. It is an AI Agent simulation framework that demonstrates Object-Oriented Programming, RegEx Validation, File Handling, REST APIs, PyQt6, and Streamlit Data Visualizations."*

### Step 2: Show Login & RegEx Validation (`python main.py`)
> *"First, when launching the app, the Login & Registration system (`auth.py`) appears. It uses Python's `re` module to validate all inputs using 7 regex functions (`fullmatch`, `match`, `search`, `findall`, `compile`, `sub`, `split`) with custom exception handling."*
> 
> **Action**: Launch `python main.py`. Try logging in with username `edrin` and password `Password123!`.

### Step 3: Show PyQt6 Desktop GUI & Agent Observability
> *"Next, the main desktop GUI (`cli.py`) opens. It satisfies Requirement #3 by using 4 layout managers (`QVBoxLayout`, `QHBoxLayout`, `QFormLayout`, `QSplitter`), 5 widgets, 5 signal-slot connections, and 3 event handler overrides like Esc key cancelling and close confirmation dialogs."*
> 
> **Action**: Click `📎 Attach`, pick `data/records.txt`, and click Send. Point out the **Execution Trace** panel showing real-time tool selection!

### Step 4: Show File Handling Demo (`python file_demo.py`)
> *"For the File Operations assignment, `file_manager.py` implements functions using file modes `w`, `r`, `a`, `r+`, `w+`, file methods `seek()`, `tell()`, `readlines()`, `writelines()`, and RegEx validation."*
> 
> **Action**: Run `python file_demo.py` in terminal to show the automated verification output.

### Step 5: Show Flask REST API & Streamlit Dashboard
> *"Finally, `server.py` provides a Flask REST API (`GET`, `POST` 201, `PUT`, `DELETE`), tested via `client_demo.py`, while `app_streamlit.py` provides a live web analytics dashboard with Plotly charts."*
> 
> **Action**: Run `python server.py` / `python client_demo.py` or open `app_streamlit.py`.
