"""
roadmap_generator.py
Handles learning path generation using Google Gemini AI, with a smart offline
Demo Mode fallback when no API key is provided.
Also provides resource curation and study scheduling routines shared with the MCP server.
"""

import os
import math
from typing import Tuple, Optional, Dict, Any


def build_system_prompt() -> str:
    return (
        "You are an expert AI curriculum designer, senior tech mentor, and educational architect. "
        "Your mission is to generate highly structured, deeply practical, and engaging personalized learning roadmaps. "
        "Always tailor your advice directly to the student's background level, study timeframe, and ultimate goal. "
        "Format your output in clean, professional GitHub-flavored Markdown using emojis, callouts, tables, and clear headings."
    )


def build_user_prompt(
    student_name: str,
    skill: str,
    level: str,
    duration_days: int,
    daily_hours: float,
    learning_goal: str
) -> str:
    total_hours = round(duration_days * daily_hours, 1)
    weeks = max(1, math.ceil(duration_days / 7))
    
    return f"""
Please generate a comprehensive, personalized Learning Roadmap for:
- **Student Name:** {student_name}
- **Target Skill:** {skill}
- **Current Experience Level:** {level}
- **Total Duration:** {duration_days} days ({weeks} week{'s' if weeks > 1 else ''})
- **Daily Commitment:** {daily_hours} hours/day (Total commitment: ~{total_hours} hours)
- **Primary Learning Goal:** {learning_goal}

Format the response in rich, clean Markdown with the following exact sections:

# 🎓 Personalized Learning Roadmap: {skill}
*Prepared for {student_name} • Commitment: {daily_hours} hrs/day ({duration_days} Days / ~{total_hours} Total Hours)*

---

### 1. 🎯 Personalized Learning Objectives
- Clearly list 4-5 measurable, actionable outcomes {student_name} will achieve by completing this roadmap.

### 2. 🗓️ Structured Weekly Study Plan
- Break down the roadmap into {weeks} week(s).
- For each week, provide:
  - **Week Title & Focus Theme**
  - **Daily Focus & Allocation** (Day-by-day distribution)
  - **Milestone Checkpoint**

### 3. 📚 Core Topics & Knowledge Modules
- Group the learning curriculum into 3 to 4 logical modules (from fundamentals to advanced concepts suited for the {level} level).
- Under each module, list essential concepts, key tools, and best practices.

### 4. 💻 Hands-on Practice Exercises
- Provide 3-4 specific, hands-on coding/practical exercises that reinforce learning.
- Include estimated completion time and clear success criteria.

### 5. 🏆 Capstone Mini-Project Idea
- **Project Name:** An engaging, portfolio-worthy project name.
- **Problem Statement:** What real-world problem does it solve?
- **Key Features & Deliverables:** 3-4 concrete features to implement.
- **Tech Stack & Libraries:** Recommended tools to use.
- **Step-by-step Implementation Milestones:** How to build it in the final phase.

### 6. 🚀 Recommended Next Steps & Career Advancement
- What to explore after completing this roadmap (certifications, advanced tools, community resources, portfolio tips).
"""


def verify_gemini_api_key(api_key: str, model_name: str = "gemini-3.8-flash") -> Tuple[bool, str]:
    """
    Performs a lightweight 1-token health check to verify the Gemini API key.
    Never exposes or logs the raw API key.
    """
    clean_key = (api_key or "").strip()
    if not clean_key:
        return False, "API key is empty."
        
    try:
        from google import genai
        client = genai.Client(api_key=clean_key)
        
        # Test candidate models in priority order
        test_models = [model_name, "gemini-3.8-flash", "gemini-3.5-flash-lite", "gemini-3.1-pro-preview"]
        # Deduplicate while preserving order
        unique_models = list(dict.fromkeys([m for m in test_models if m]))
        
        last_error = ""
        for model in unique_models:
            try:
                res = client.models.generate_content(
                    model=model,
                    contents="Say OK",
                )
                if res and res.text:
                    return True, f"Success! Model '{model}' responded successfully."
            except Exception as e:
                last_error = str(e)
                continue
                
        # Sanitize error to avoid showing raw key if ever embedded
        safe_error = last_error.replace(clean_key, "[REDACTED_API_KEY]")
        return False, f"Gemini connection failed: {safe_error}"
    except Exception as e:
        safe_error = str(e).replace(clean_key, "[REDACTED_API_KEY]")
        return False, f"SDK initialization error: {safe_error}"


def generate_with_gemini(
    student_name: str,
    skill: str,
    level: str,
    duration_days: int,
    daily_hours: float,
    learning_goal: str,
    api_key: str,
    model_name: Optional[str] = None
) -> Tuple[str, Optional[str]]:
    """
    Attempts to generate the roadmap using Google GenAI SDK.
    Returns (generated_text, error_message).
    """
    prompt = build_user_prompt(
        student_name=student_name,
        skill=skill,
        level=level,
        duration_days=duration_days,
        daily_hours=daily_hours,
        learning_goal=learning_goal
    )
    
    clean_key = (api_key or "").strip()
    
    # Try using google-genai
    try:
        from google import genai
        from google.genai import types
        
        client = genai.Client(api_key=clean_key)
        
        # Prepare system instruction and generation config
        config = types.GenerateContentConfig(
            system_instruction=build_system_prompt(),
            temperature=0.7
        )
        
        # Candidate models list, prioritizing user-selected model
        preferred_model = model_name or "gemini-3.8-flash"
        candidate_models = [preferred_model, "gemini-3.8-flash", "gemini-3.5-flash-lite", "gemini-3.1-pro-preview"]
        unique_candidates = list(dict.fromkeys([m for m in candidate_models if m]))
        
        last_error = None
        for model in unique_candidates:
            try:
                response = client.models.generate_content(
                    model=model,
                    contents=prompt,
                    config=config
                )
                if response and response.text:
                    return response.text, None
            except Exception as e:
                last_error = str(e).replace(clean_key, "[REDACTED_API_KEY]")
                continue
                
        if last_error:
            return "", f"Gemini API Error: {last_error}"
            
    except ImportError:
        pass
    except Exception as e:
        safe_err = str(e).replace(clean_key, "[REDACTED_API_KEY]")
        return "", f"Gemini connection error: {safe_err}"
        
    # Fallback to google.generativeai if installed
    try:
        import google.generativeai as legacy_genai
        legacy_genai.configure(api_key=clean_key)
        model = legacy_genai.GenerativeModel("gemini-3.8-flash")
        response = model.generate_content(prompt)
        if response and response.text:
            return response.text, None
    except Exception as e:
        safe_err = str(e).replace(clean_key, "[REDACTED_API_KEY]")
        return "", f"Legacy Gemini Error: {safe_err}"

    return "", "Could not initialize Gemini client. Check dependencies."


def generate_demo_roadmap(
    student_name: str,
    skill: str,
    level: str,
    duration_days: int,
    daily_hours: float,
    learning_goal: str
) -> str:
    """
    Generates a rich, highly tailored offline roadmap when no API key is provided.
    Never returns placeholder Lorem Ipsum - generates genuine curriculum.
    """
    total_hours = round(duration_days * daily_hours, 1)
    weeks = max(1, math.ceil(duration_days / 7))
    skill_clean = skill.strip().title() or "Modern AI & Software Development"
    
    # Determine skill category for contextual tailoring
    skill_lower = skill.lower()
    
    if "python" in skill_lower:
        domain = "Python Programming & Software Engineering"
        topics_mod1 = ["Variables, Data Types, Conditionals, and Loops", "Functions, Scope, and Lambda Expressions", "Lists, Dictionaries, Sets, and Tuples"]
        topics_mod2 = ["Object-Oriented Programming (Classes & Inheritance)", "File I/O, JSON Parsing, and Exception Handling", "Virtual Environments and Package Management (pip, uv)"]
        topics_mod3 = ["Working with APIs and Requests", "Data Manipulation with Pandas & NumPy", "Writing Unit Tests with pytest"]
        project_name = f"Smart Task Automation & Data Analyzer in {skill_clean}"
        project_desc = "A CLI and web-enabled tool that ingests external API data, processes metrics, and generates automated summary reports."
        project_stack = "Python 3.10+, Requests, Pandas, Streamlit"
    elif "mcp" in skill_lower or "model context protocol" in skill_lower:
        domain = "Model Context Protocol (MCP) & AI Tool Integration"
        topics_mod1 = ["Core MCP Architecture: Hosts, Clients, and Servers", "JSON-RPC 2.0 Protocol & Stdio vs SSE Transports", "Tool Definitions, Resources, and Prompts in MCP"]
        topics_mod2 = ["Building your First Custom MCP Server in Python with MCPServer", "Schema Validation with Pydantic and Type Hints", "Connecting MCP Servers to Claude Desktop & Antigravity"]
        topics_mod3 = ["Handling Error States, Rate Limits, and Security", "Authentication and State Management in MCP", "Packaging and Distributing MCP Servers"]
        project_name = f"Custom Intelligent Knowledge MCP Server"
        project_desc = "A production-grade MCP Server exposing custom data tools and dynamic system prompts for AI agents."
        project_stack = "Python 3.10+, Official MCP SDK (mcp), Pydantic, Claude Desktop/Antigravity"
    elif "machine learning" in skill_lower or "ml" in skill_lower or "data science" in skill_lower:
        domain = "Machine Learning & Applied Data Science"
        topics_mod1 = ["Exploratory Data Analysis (EDA) and Visualization", "Feature Engineering, Scaling, and Preprocessing", "Supervised Learning: Regression & Classification Algorithms"]
        topics_mod2 = ["Model Evaluation Metrics: ROC-AUC, F1-Score, Cross-Validation", "Unsupervised Learning: Clustering & PCA", "Tree-based Ensembles (Random Forest, XGBoost)"]
        topics_mod3 = ["Model Persistence & Serialisation (joblib/pickle)", "Deploying ML Models as REST APIs / Streamlit Apps", "MLOps Fundamentals and Monitoring"]
        project_name = f"End-to-End Predictive Analytics Engine"
        project_desc = "A complete ML pipeline that trains on real-world datasets and exposes interactive predictions through a web UI."
        project_stack = "Scikit-Learn, Pandas, Seaborn, Streamlit, Joblib"
    elif "web" in skill_lower or "react" in skill_lower or "frontend" in skill_lower or "fullstack" in skill_lower:
        domain = "Modern Web Application Development"
        topics_mod1 = ["Semantic HTML5, Modern CSS Layouts (Flexbox/Grid), and Responsive Design", "JavaScript ES6+ (Async/Await, Promises, Closures, DOM Manipulation)", "Modern Build Tooling (Vite, npm/pnpm)"]
        topics_mod2 = ["Component-Driven Architecture, State Management, and Props", "RESTful API Integration & Error Handling", "Routing, Authentication, and Local Storage"]
        topics_mod3 = ["Performance Optimization, Accessibility (a11y), and SEO", "State Containers, Hooks, and Reusable UI Components", "Deployment & CI/CD on Modern Cloud Platforms"]
        project_name = f"Interactive AI Dashboard & Workspace"
        project_desc = "A responsive web application featuring real-time state, dark/light theme, and seamless API integrations."
        project_stack = "React / Modern JS, TailwindCSS, REST API, Vercel/Netlify"
    elif "prompt" in skill_lower or "generative ai" in skill_lower or "llm" in skill_lower:
        domain = "Generative AI Engineering & Prompt Design"
        topics_mod1 = ["LLM Architecture Fundamentals: Tokens, Temperature, Top-p, Context Windows", "Prompt Engineering Frameworks (Few-shot, Chain-of-Thought, ReAct)", "System Prompt Architecture and Role Conditioning"]
        topics_mod2 = ["Retrieval-Augmented Generation (RAG) Architecture & Vector Embeddings", "Structured Outputs, JSON Schema Enforcement, and Guardrails", "Multi-turn Conversations and Memory Management"]
        topics_mod3 = ["Function Calling and Tool Use with Gemini & MCP Protocols", "Evaluation Metrics for Generative AI Applications", "Deploying AI Apps with Streamlit and FastAPI"]
        project_name = f"Autonomous AI Assistant with Tool Execution"
        project_desc = "An interactive AI copilot that accepts user queries, searches knowledge bases, and executes automated functions."
        project_stack = "Google Gemini API, Python, Streamlit, MCP Tools"
    else:
        domain = f"Mastering {skill_clean}"
        topics_mod1 = [f"Foundational Principles & Core Concepts of {skill_clean}", f"Environment Setup, Essential Tools, and Syntax/Basics", f"Standard Workflows and Common Design Patterns"]
        topics_mod2 = [f"Intermediate Implementations & Real-World Application in {skill_clean}", f"Debugging, Troubleshooting, and Error Handling Techniques", f"Best Practices, Performance Considerations, and Architecture"]
        topics_mod3 = [f"Advanced Techniques and Production-Grade Workflows", f"Integrating {skill_clean} with Modern Industry Toolchains", f"Testing, Automation, and Scalable Maintenance"]
        project_name = f"Production-Ready {skill_clean} Capstone Application"
        project_desc = f"A portfolio-ready system applying all core and intermediate concepts of {skill_clean} to solve a tangible problem."
        project_stack = f"{skill_clean}, Python, Git, Markdown Documentation"

    # Generate Weekly breakdown
    weekly_sections = []
    for w in range(1, weeks + 1):
        if w == 1:
            theme = "Foundations, Setup & Core Principles"
            focus_a = "Day 1-3: Environment installation, core syntax, and establishing foundational mental models."
            focus_b = "Day 4-7: Hands-on micro-tasks, running first scripts/modules, and debugging initial errors."
            checkpoint = f"Complete initial code drills with 0 errors and push your learning notes repository to Git."
        elif w == 2 and w < weeks:
            theme = "Deepening Skills & Intermediate Problem Solving"
            focus_a = "Day 8-11: Structuring modular components, exploring libraries, and handling edge cases."
            focus_b = "Day 12-14: Building intermediate exercises and connecting external services/APIs."
            checkpoint = "Successfully build a working prototype script that solves a repetitive task."
        elif w == weeks:
            theme = "Integration, Capstone Project & Polish"
            focus_a = f"Day {((w-1)*7)+1}-{min(duration_days, ((w-1)*7)+4)}: Architect and implement the {project_name}."
            focus_b = f"Day {min(duration_days, ((w-1)*7)+5)}-{duration_days}: Code cleanup, documentation, testing, and portfolio deployment."
            checkpoint = f"Deploy your finished project and prepare a demonstration walkthrough!"
        else:
            theme = f"Advanced Capabilities & Real-World Case Studies (Phase {w})"
            focus_a = f"Day {((w-1)*7)+1}-{((w-1)*7)+3}: Advanced architecture patterns and high-efficiency tooling."
            focus_b = f"Day {((w-1)*7)+4}-{((w-1)*7)+7}: Integration testing, performance tuning, and peer review."
            checkpoint = f"Mastery test: Solve an end-to-end challenge in under 60 minutes."
            
        weekly_sections.append(f"""
#### 🗓️ Week {w}: {theme}
- **Daily Schedule:**
  - 🔹 {focus_a}
  - 🔹 {focus_b}
- **Target Time:** {round(daily_hours * 7, 1)} hours for this week
- **Milestone Checkpoint:** ✅ {checkpoint}
""")

    weeks_text = "\n".join(weekly_sections)
    
    # Format practice exercises
    exercises = f"""
1. **Interactive Sandbox Challenge (Estimated: {daily_hours} hr)**
   - Build a standalone module that implements the primary concepts from Module 1.
   - *Success Criteria:* Code is clean, well-commented, and executes without runtime warnings.

2. **Error Recovery & Debugging Lab (Estimated: {daily_hours * 1.5:.1f} hrs)**
   - Intentionally introduce 3 common edge-case scenarios into your project and write unit tests / assertions to gracefully handle them.
   - *Success Criteria:* System logs meaningful error messages rather than crashing.

3. **External Integration Lab (Estimated: {daily_hours * 2:.1f} hrs)**
   - Connect your {skill_clean} project to an external data source or API endpoint and parse structured results.
   - *Success Criteria:* Successfully fetch and render live data within the terminal or web UI.
"""

    # Pre-format topics to ensure compatibility with Python 3.10 and older
    mod1_text = "\n".join(f"- ▫️ {t}" for t in topics_mod1)
    mod2_text = "\n".join(f"- ▫️ {t}" for t in topics_mod2)
    mod3_text = "\n".join(f"- ▫️ {t}" for t in topics_mod3)

    return f"""# 🎓 Personalized Learning Roadmap: {skill_clean}
*Prepared for **{student_name}** • Commitment: **{daily_hours} hrs/day** ({duration_days} Days / ~{total_hours} Total Hours)*

> [!NOTE]
> **Mode: Smart Demo Generator** (Fast, tailored offline curriculum). To unlock live generative AI responses, enter your Google Gemini API key in the sidebar.

---

### 1. 🎯 Personalized Learning Objectives
By following this personalized curriculum, **{student_name}** will be able to:
- 📌 **Master Foundational Competencies:** Develop an intuitive understanding of core principles in **{skill_clean}** starting from the **{level}** level.
- 📌 **Apply Industry Best Practices:** Write idiomatic, well-structured, and maintainable code adhering to standard conventions.
- 📌 **Achieve Primary Goal:** Directly accomplish the target objective: *" {learning_goal} "*.
- 📌 **Ship a Portfolio Project:** Design, build, and deploy an original capstone project (**{project_name}**) to demonstrate capability to recruiters and peers.
- 📌 **Build Autonomous Problem Solving:** Confidently navigate technical documentation, resolve real-world errors, and adapt to emerging tools.

---

### 2. 🗓️ Structured Weekly Study Plan
Total Duration: **{duration_days} Days** (~**{weeks} Weeks**) | Total Estimated Effort: **~{total_hours} Hours**

{weeks_text}

---

### 3. 📚 Core Topics & Knowledge Modules

#### 📦 Module 1: Core Fundamentals & Workflow Setup
{mod1_text}

#### 📦 Module 2: Applied Techniques & Architecture
{mod2_text}

#### 📦 Module 3: Production Mastery & Optimization
{mod3_text}

---

### 4. 💻 Hands-on Practice Exercises
{exercises}

---

### 5. 🏆 Capstone Mini-Project Idea

- **Project Title:** `{project_name}`
- **Problem Statement:** {project_desc}
- **Recommended Tech Stack:** {project_stack}
- **Key Features to Implement:**
  1. *User Input & Configuration:* Intuitive parameters allowing users to run custom workflows.
  2. *Core Processing Logic:* Robust algorithms implementing {skill_clean} standards.
  3. *Error Handling & Logging:* Graceful recovery from missing inputs or invalid network states.
  4. *Polished Output / UI:* Clean presentation layer showcasing actionable results.
- **Implementation Strategy:**
  - **Step 1:** Draft the system architecture and list required packages.
  - **Step 2:** Build the minimal working prototype (MVP) focusing on the core business logic.
  - **Step 3:** Add defensive validation, enhance user experience, and write a clear `README.md`.

---

### 6. 🚀 Recommended Next Steps & Career Advancement
- 🌐 **Publish on GitHub:** Create a public GitHub repository with an eye-catching `README.md`, badges, and demo GIF.
- 🤝 **Engage with the Community:** Share your progress on LinkedIn and Discord/Reddit developer forums to gain feedback.
- ⚙️ **MCP & AI Tooling:** Connect your project to an MCP (Model Context Protocol) Server so AI agents like Claude or Antigravity can interact with it directly.
- 📜 **Next Skill to Pair:** Complement **{skill_clean}** by learning Cloud Deployment (Docker/Streamlit Community Cloud) and CI/CD pipelines.
"""


def get_learning_resources_data(skill: str, level: str = "Beginner") -> str:
    """
    Curates high-value, vetted learning resources for a given skill and level.
    Used both in the application and by the MCP Server tool 'get_learning_resources'.
    """
    skill_clean = skill.strip().title() or "Software Development"
    skill_lower = skill.lower()
    
    if "mcp" in skill_lower or "model context" in skill_lower:
        return f"""### 📚 Curated Learning Resources: Model Context Protocol (MCP) ({level})

1. **Official MCP Documentation & Specification**
   - *URL:* https://modelcontextprotocol.io
   - *Description:* Core protocol specification, JSON-RPC schema, Stdio/SSE transport documentation.
2. **Official Python MCP SDK**
   - *Repository:* https://github.com/modelcontextprotocol/python-sdk
   - *Description:* Official SDK providing `MCPServer`, tool registration decorators, and client transports.
3. **Anthropic MCP Quickstart Guides**
   - *URL:* https://docs.anthropic.com/en/docs/agents-and-tools/mcp
   - *Description:* Walkthroughs for connecting custom MCP servers to Claude Desktop and AI clients.
4. **Community MCP Servers Directory**
   - *Repository:* https://github.com/modelcontextprotocol/servers
   - *Description:* Reference implementations for Postgres, Git, Filesystem, and Web Search servers.
"""
    elif "python" in skill_lower:
        return f"""### 📚 Curated Learning Resources: {skill_clean} ({level})

1. **Official Python Documentation & Tutorial**
   - *URL:* https://docs.python.org/3/tutorial/
   - *Description:* The definitive, beginner-to-advanced guide to Python's syntax, data structures, and standard library.
2. **Real Python (Tutorials & Deep Dives)**
   - *URL:* https://realpython.com
   - *Description:* Practical, high-quality articles covering virtual environments, OOP, APIs, and best practices.
3. **Automate the Boring Stuff with Python**
   - *URL:* https://automatetheboringstuff.com
   - *Description:* Practical task automation (file manipulation, web scraping, Excel/CSV manipulation).
4. **Streamlit Official Documentation**
   - *URL:* https://docs.streamlit.io
   - *Description:* Interactive app development, state management, and dashboard deployment.
"""
    elif "machine learning" in skill_lower or "data science" in skill_lower:
        return f"""### 📚 Curated Learning Resources: {skill_clean} ({level})

1. **Scikit-Learn User Guide & API**
   - *URL:* https://scikit-learn.org/stable/user_guide.html
   - *Description:* Industry standard tutorials on supervised, unsupervised algorithms and model evaluation.
2. **Kaggle Learn Micro-Courses**
   - *URL:* https://www.kaggle.com/learn
   - *Description:* Fast, hands-on notebooks covering Pandas, Intro to ML, Intermediate ML, and Feature Engineering.
3. **Fast.ai - Practical Deep Learning for Coders**
   - *URL:* https://course.fast.ai
   - *Description:* Top-down, practical machine learning with PyTorch.
"""
    else:
        return f"""### 📚 Curated Learning Resources: {skill_clean} ({level})

1. **Official Documentation & Guides for {skill_clean}**
   - *Description:* Always prioritize the primary language/framework documentation for idiomatic patterns.
2. **GitHub Awesome Lists for {skill_clean}**
   - *Search Query:* `awesome-{skill_clean.lower().replace(' ', '-')}` on GitHub.
   - *Description:* Community-curated collection of top libraries, boilerplates, and tutorials.
3. **Interactive Practice & Sandbox Drills**
   - *Platforms:* Exercism, LeetCode, freeCodeCamp, or official interactive playgrounds.
4. **YouTube & Developer Community Forums**
   - *Communities:* Stack Overflow, Reddit (r/learnprogramming), Discord developer servers.
"""


def create_study_schedule_data(skill: str, duration_days: int = 7, daily_hours: float = 2.0) -> str:
    """
    Generates a structured daily time-block schedule for studying a skill.
    Used both in the application and by the MCP Server tool 'create_daily_study_schedule'.
    """
    skill_clean = skill.strip().title() or "Target Skill"
    duration = max(1, min(duration_days, 60))
    daily_h = max(0.5, min(daily_hours, 12.0))
    
    # Calculate recommended Pomodoro blocks (25m study + 5m break)
    study_minutes = int(daily_h * 60)
    pomodoros = max(1, study_minutes // 30)
    
    schedule_blocks = []
    schedule_blocks.append(f"### ⏰ Daily Study Schedule: {skill_clean}")
    schedule_blocks.append(f"*Target: **{daily_h} hours/day** across **{duration} days** (~{round(daily_h * duration, 1)} total hours)*\n")
    schedule_blocks.append("#### 🍅 Recommended Daily Pomodoro Breakdown:")
    schedule_blocks.append(f"- **Block 1 (First 25% of time):** Conceptual Review & Active Reading (Documentation, video lessons).")
    schedule_blocks.append(f"- **Block 2 (Next 50% of time):** Hands-on Coding Drills & Live Implementation.")
    schedule_blocks.append(f"- **Block 3 (Final 25% of time):** Code Refactoring, Debugging & Summary Journaling.\n")
    
    schedule_blocks.append("#### 📅 Day-by-Day Agenda:")
    for day in range(1, duration + 1):
        if day == 1:
            task = f"Setup local workspace, verify dependencies, and outline the {skill_clean} roadmap."
        elif day == duration:
            task = f"Final project review, code cleanup, git commit, and reflection on achieved goals."
        elif day % 7 == 0:
            task = "Weekly Review Day: Review past notes, fix bugs, and refactor previous exercises."
        elif day % 2 == 1:
            task = f"Learn core concepts and complete interactive coding drills for {skill_clean}."
        else:
            task = f"Build and expand practical mini-modules for the {skill_clean} project."
            
        schedule_blocks.append(f"- **Day {day:02d}:** {task} *(Allocated: {daily_h} hrs)*")
        
    return "\n".join(schedule_blocks)


def generate_learning_roadmap(
    student_name: str,
    skill: str,
    level: str,
    duration_days: int,
    daily_hours: float,
    learning_goal: str,
    api_key: Optional[str] = None,
    model_name: Optional[str] = None
) -> Tuple[str, bool, Optional[str]]:
    """
    Main generator interface.
    Returns:
        (roadmap_markdown_content, is_demo_mode, error_message)
    """
    # Clean inputs
    student_name = student_name.strip() or "Learner"
    skill = skill.strip() or "Python Programming"
    level = level.strip() or "Beginner"
    learning_goal = learning_goal.strip() or f"Master {skill} and build real-world applications."
    
    # Check for API key (argument or environment variable)
    resolved_key = (api_key or os.getenv("GEMINI_API_KEY", "")).strip()
    
    if resolved_key:
        content, error = generate_with_gemini(
            student_name=student_name,
            skill=skill,
            level=level,
            duration_days=duration_days,
            daily_hours=daily_hours,
            learning_goal=learning_goal,
            api_key=resolved_key,
            model_name=model_name
        )
        if content:
            return content, False, None
        else:
            # Fallback to demo mode if API call failed
            demo_content = generate_demo_roadmap(
                student_name=student_name,
                skill=skill,
                level=level,
                duration_days=duration_days,
                daily_hours=daily_hours,
                learning_goal=learning_goal
            )
            return demo_content, True, f"AI generation encountered an issue ({error}). Loaded high-fidelity Demo Mode instead."
    else:
        # No API key provided -> Return Demo Mode
        demo_content = generate_demo_roadmap(
            student_name=student_name,
            skill=skill,
            level=level,
            duration_days=duration_days,
            daily_hours=daily_hours,
            learning_goal=learning_goal
        )
        return demo_content, True, None
