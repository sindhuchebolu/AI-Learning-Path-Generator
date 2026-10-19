# 🎓 AI Learning Path Generator

A production-grade, full-stack AI web application and **Model Context Protocol (MCP)** server built with **Python**, **Streamlit**, **Google Gemini AI**, and the **official Python MCP SDK (`mcp`)**.

The **AI Learning Path Generator** transforms any technology or career goal into a structured, step-by-step learning roadmap tailored to the student's background, available schedule, and learning objectives. It functions both as an interactive web app and as an autonomous **MCP Server** that AI agents (such as Claude Desktop, Antigravity, or Cursor) can query over standard I/O (`stdio`).

---

## 🌟 Key Features

1. **🎨 Modern & Responsive User Interface:**
   - Deep indigo gradient hero banner, responsive metrics cards (Total Days, Daily Commitment, Total Investment Hours, Target Level), and clean typography.
   - Built natively using Streamlit with custom CSS styling and responsive layouts.

2. **📋 Personalized Input Controls:**
   - **Student Name:** Person-specific curriculum and milestones.
   - **Target Skill:** Any technical or creative skill (e.g., Python, Model Context Protocol, Data Science, Web Development).
   - **Current Experience Level:** Beginner, Intermediate, or Advanced.
   - **Learning Duration:** Total days (from 3 to 180 days).
   - **Daily Commitment:** Dedicated hours per day (0.5 to 12.0 hours).
   - **Primary Goal:** Specific objective (e.g. build an MCP tool, land a junior developer role, pass certification).

3. **🧠 Dual AI Engine (Live Gemini + Offline Smart Demo):**
   - **Live AI Mode:** Generates unique, dynamic roadmaps using Google's current Gemini models (`gemini-3.8-flash`, `gemini-3.5-flash-lite`, `gemini-3.1-pro-preview`) with structured system prompts and temperature control.
   - **Connection Health Check:** Built-in "🧪 Test API Connection" button in the sidebar to verify API key validity with a lightweight test before running full generation.
   - **Smart Demo Mode:** If an API key is not configured or quota is exceeded, the app automatically falls back to an intelligent offline generator tailored to the student's inputs. Zero blockers during testing or presentations!

4. **🛠️ Genuine Model Context Protocol (MCP) Server:**
   - Implemented via the official Python MCP SDK (`mcp.server.mcpserver.MCPServer`).
   - Exposes 3 standard MCP Tools over JSON-RPC 2.0 `stdio`:
     - `generate_learning_plan`: Generates comprehensive, personalized roadmaps.
     - `get_learning_resources`: Returns curated, vetted documentation, tutorials, and repositories.
     - `create_daily_study_schedule`: Generates daily time-block study schedules with Pomodoro breakdowns.
   - Exposes an MCP Resource (`learning://curriculum-catalog`) and an MCP Prompt (`study_advisor`).
   - Includes a dedicated test client (`test_mcp_client.py`) with 7 automated verification tests.

5. **⚡ Interactive Extras:**
   - **Milestone Checklist Tab:** Allows learners to check off weekly goals as they study.
   - **MCP Integration Tab:** Explains the protocol, lets users run MCP tools directly from the UI, and provides copy-ready configuration for Claude Desktop and Antigravity.
   - **One-Click Export:** Download the entire roadmap as a clean Markdown (`.md`) file.
   - **Quick Presets:** Instant loading of popular scenarios for quick demos.

6. **🔒 Secure by Design:**
   - API keys are never hardcoded, logged, or printed. Keys can be set in a `.env` file or entered dynamically into the password field in the UI.

---

## 📁 Project Architecture & File Structure

```text
AI-Learning-Path-Generator/
│
├── app.py                  # Main Streamlit web application & UI
├── mcp_server.py           # Official Model Context Protocol (MCP) Server (Stdio)
├── test_mcp_client.py      # Automated MCP client verification test suite (7 tests)
├── roadmap_generator.py    # AI curriculum engine (Gemini API + Smart Demo fallback + MCP routines)
├── requirements.txt        # Python dependencies (streamlit, google-genai, python-dotenv, mcp)
├── .env.example            # Environment variables template
├── .gitignore              # Ignored files (virtual environment, cache, .env)
├── run.bat                 # 1-Click launcher for Windows Command Prompt
├── run.ps1                 # PowerShell launcher script
└── README.md               # Complete project documentation
```

---

## 🚀 How to Run on Windows (PowerShell Commands)

### 1. Open Terminal and Navigate to the Project
```powershell
cd c:\Users\sindh\OneDrive\Desktop\AI-Learning-Path-Generator
```

---

### 2. Activate the Virtual Environment
```powershell
.\.venv\Scripts\Activate.ps1
```

---

### 3. Install Required Packages
```powershell
pip install -r requirements.txt
```

---

### 4. (Optional) Configure Your Gemini API Key Securely
You can test the app immediately in **Smart Demo Mode** without an API key.

To enable live Google Gemini AI generation:
1. Create your `.env` file from the template:
   ```powershell
   Copy-Item .env.example .env
   ```
2. Open `.env` in Notepad and insert your key:
   ```env
   GEMINI_API_KEY=AIzaSy...your_actual_key_here
   ```
*(Alternatively, you can type or paste the API key directly into the password field in the web sidebar and click "🧪 Test API Connection".)*

---

### 5. Run the MCP Verification Tests
To verify all 7 Model Context Protocol tools, resources, and prompts:
```powershell
.\.venv\Scripts\python.exe test_mcp_client.py
```
*Expected result:*
```text
=================================================================
🎉 ALL 7 MCP PROTOCOL TESTS COMPLETED AND VERIFIED 100% PASSING!
=================================================================
```

---

### 6. Start the MCP Server Directly (Stdio Mode)
To run the MCP server so AI hosts (like Claude Desktop or Antigravity) can connect:
```powershell
.\.venv\Scripts\python.exe mcp_server.py
```

---

### 7. Start the Streamlit Web Application
```powershell
.\run.ps1
```
Or directly:
```powershell
.\.venv\Scripts\streamlit.exe run app.py
```

The app will open automatically in your browser at:  
👉 **`http://localhost:8501`**

---

## 🔌 Connecting to Claude Desktop / Antigravity as an MCP Server

To enable Claude Desktop or Antigravity to use these learning tools, add this configuration block to your MCP configuration file (e.g., `%APPDATA%\Claude\claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "learning-path-generator": {
      "command": "c:\\Users\\sindh\\OneDrive\\Desktop\\AI-Learning-Path-Generator\\.venv\\Scripts\\python.exe",
      "args": [
        "c:\\Users\\sindh\\OneDrive\\Desktop\\AI-Learning-Path-Generator\\mcp_server.py"
      ],
      "env": {
        "GEMINI_API_KEY": "YOUR_GEMINI_API_KEY_HERE"
      }
    }
  }
}
```

Once configured, your AI assistant can directly call:
- `generate_learning_plan`
- `get_learning_resources`
- `create_daily_study_schedule`

---

## 🧪 Test Results & Verification Record

All tests were performed directly in the project environment:

| Test Item | Command / Procedure | Result |
| :--- | :--- | :--- |
| **Python Syntax Check** | `python -m py_compile app.py roadmap_generator.py mcp_server.py test_mcp_client.py` | ✅ **PASS** (Code 0, zero syntax errors) |
| **Offline Demo Mode** | `generate_learning_roadmap()` with no API key | ✅ **PASS** (Generated 5,400+ char roadmap) |
| **Defensive Error Handling** | `generate_learning_roadmap()` with invalid API key | ✅ **PASS** (Caught 400 error, fell back to Demo) |
| **Key Health Check** | `verify_gemini_api_key()` with invalid key | ✅ **PASS** (Reported sanitized error message) |
| **MCP Tool Discovery** | `mcp.list_tools()` via test client | ✅ **PASS** (Discovered all 3 registered tools) |
| **MCP Tool: Plan** | `mcp.call_tool('generate_learning_plan')` | ✅ **PASS** (5,417 chars returned via protocol) |
| **MCP Tool: Resources** | `mcp.call_tool('get_learning_resources')` | ✅ **PASS** (Curated resources returned) |
| **MCP Tool: Schedule** | `mcp.call_tool('create_daily_study_schedule')` | ✅ **PASS** (Daily Pomodoro agenda returned) |
| **MCP Input Validation** | `mcp.call_tool('generate_learning_plan', {'skill': ''})` | ✅ **PASS** (Rejected with validation error) |
| **MCP Resource Read** | `mcp.read_resource('learning://curriculum-catalog')` | ✅ **PASS** (Read domain catalog) |
| **MCP Prompt Retrieval** | `mcp.get_prompt('study_advisor')` | ✅ **PASS** (Retrieved dynamic prompt) |
| **MCP Wire Protocol** | JSON-RPC 2.0 `initialize` over `stdio` subprocess | ✅ **PASS** (Returned protocol capabilities) |
| **Streamlit Server** | `streamlit run app.py` on port 8501 | ✅ **PASS** (`HTTP 200 OK`) |

---

## 📄 License
MIT License. Free to use, adapt, and build upon for educational and workshop purposes!
