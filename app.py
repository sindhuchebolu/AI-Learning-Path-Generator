import os
import streamlit as st
from dotenv import load_dotenv
from roadmap_generator import (
    generate_learning_roadmap,
    verify_gemini_api_key,
    get_learning_resources_data,
    create_study_schedule_data
)

# Load environment variables from .env if present
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="AI Learning Path Generator",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for modern, professional styling
CUSTOM_CSS = """
<style>
    /* Font and general canvas styling */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    /* Main Container Padding */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 3.5rem;
        max-width: 1200px;
    }

    /* Hero Banner */
    .hero-container {
        background: linear-gradient(135deg, #1e1b4b 0%, #312e81 40%, #4338ca 100%);
        padding: 2.2rem 2.5rem;
        border-radius: 18px;
        color: white;
        margin-bottom: 2rem;
        box-shadow: 0 10px 25px -5px rgba(49, 46, 129, 0.25);
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    .hero-title {
        font-size: 2.3rem;
        font-weight: 800;
        letter-spacing: -0.025em;
        margin: 0 0 0.5rem 0;
        display: flex;
        align-items: center;
        gap: 0.75rem;
    }

    .hero-subtitle {
        font-size: 1.05rem;
        color: #c7d2fe;
        max-width: 800px;
        line-height: 1.55;
        margin: 0;
    }

    .hero-badges {
        margin-top: 1.1rem;
        display: flex;
        flex-wrap: wrap;
        gap: 0.5rem;
    }

    .hero-badge {
        background: rgba(255, 255, 255, 0.15);
        backdrop-filter: blur(8px);
        color: #ffffff;
        font-size: 0.8rem;
        font-weight: 600;
        padding: 0.3rem 0.75rem;
        border-radius: 9999px;
        border: 1px solid rgba(255, 255, 255, 0.2);
    }

    /* Stats & Metric Cards */
    .metric-card {
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 1.1rem;
        text-align: center;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }

    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
    }

    .metric-value {
        font-size: 1.7rem;
        font-weight: 700;
        color: #1e293b;
    }

    .metric-label {
        font-size: 0.82rem;
        font-weight: 600;
        color: #64748b;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-top: 0.2rem;
    }

    /* Sidebar cards */
    .sidebar-info-box {
        background: #f1f5f9;
        border-radius: 10px;
        padding: 1rem;
        margin-bottom: 1.2rem;
        border-left: 4px solid #4f46e5;
        font-size: 0.88rem;
        color: #334155;
    }

    /* Status Pill */
    .badge-live {
        background: #ecfdf5;
        color: #065f46;
        border: 1px solid #a7f3d0;
        font-weight: 600;
        padding: 0.2rem 0.6rem;
        border-radius: 6px;
        font-size: 0.8rem;
        display: inline-block;
    }

    .badge-demo {
        background: #fffbeb;
        color: #92400e;
        border: 1px solid #fde68a;
        font-weight: 600;
        padding: 0.2rem 0.6rem;
        border-radius: 6px;
        font-size: 0.8rem;
        display: inline-block;
    }

    /* MCP Server Pill */
    .badge-mcp {
        background: #eff6ff;
        color: #1e40af;
        border: 1px solid #bfdbfe;
        font-weight: 600;
        padding: 0.2rem 0.6rem;
        border-radius: 6px;
        font-size: 0.8rem;
        display: inline-block;
    }

    /* Results section container */
    .result-container {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 16px;
        padding: 2rem;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
    }

    /* Action buttons */
    .stButton>button {
        border-radius: 10px;
        font-weight: 600;
        padding: 0.6rem 1.2rem;
        transition: all 0.2s ease;
    }
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


def main():
    # ---------------------------------------------------------
    # Sidebar: Configurations, API Key & Workshop Notes
    # ---------------------------------------------------------
    with st.sidebar:
        st.image("https://api.iconify.design/lucide:sparkles.svg?color=%234f46e5", width=42)
        st.title("Settings & AI Config")
        
        # Check environment variable first
        env_api_key = os.getenv("GEMINI_API_KEY", "").strip()
        
        st.markdown("### 🔑 Gemini API Key")
        user_api_key = st.text_input(
            "Enter Gemini API Key (Optional)",
            type="password",
            value=env_api_key,
            help="Your key is never logged or exposed. If left empty, the application automatically runs in Demo Mode with tailored offline roadmaps."
        )

        selected_model = st.selectbox(
            "Gemini Model",
            ["gemini-3.8-flash", "gemini-3.5-flash-lite", "gemini-3.1-pro-preview"],
            index=0,
            help="Select the Google Gemini model for live roadmap generation."
        )

        # Connection health check button
        if st.button("🧪 Test API Connection", use_container_width=True):
            if not user_api_key:
                st.warning("⚠️ Enter an API key above to test connection.")
            else:
                with st.spinner("Pinging Gemini API..."):
                    is_ok, msg = verify_gemini_api_key(user_api_key, selected_model)
                    if is_ok:
                        st.success(f"✅ {msg}")
                    else:
                        st.error(f"❌ {msg}")

        # Mode status indicator
        if user_api_key:
            st.markdown(
                '<div class="badge-live">🟢 Live AI Mode Ready</div>',
                unsafe_allow_html=True
            )
            st.caption(f"Configured for live generation via `{selected_model}`.")
        else:
            st.markdown(
                '<div class="badge-demo">🟡 Smart Demo Mode Active</div>',
                unsafe_allow_html=True
            )
            st.caption("No API key entered. Running offline with smart heuristic templates.")

        st.markdown("---")
        
        # Quick Presets for Demo / Workshop
        st.markdown("### ⚡ Quick Presets")
        preset = st.selectbox(
            "Load Sample Scenario",
            [
                "-- Select a preset --",
                "Python for Data Automation",
                "Building MCP Servers in Python",
                "Full-Stack React & Node.js",
                "Prompt Engineering & LLM Apps",
                "Machine Learning Fundamentals"
            ]
        )
        
        st.markdown("---")
        
        # MCP Workshop Info Box
        st.markdown(
            """
            <div class="sidebar-info-box">
                <strong>🛠️ MCP Server Active</strong><br>
                Official Model Context Protocol Server implemented via <code>mcp_server.py</code>.<br>
                <span class="badge-mcp">Stdio Transport Ready</span>
            </div>
            """,
            unsafe_allow_html=True
        )

        st.caption("v1.1.0 • Built with Python, Streamlit & MCP")

    # ---------------------------------------------------------
    # Preset Handlers
    # ---------------------------------------------------------
    default_name = "Alex Johnson"
    default_skill = "Python for AI Development"
    default_level = "Beginner"
    default_duration = 14
    default_hours = 2.0
    default_goal = "Build practical automation tools and prepare for the MCP Workshop."

    if preset == "Python for Data Automation":
        default_skill = "Python for Data Automation"
        default_level = "Beginner"
        default_duration = 14
        default_hours = 2.0
        default_goal = "Automate Excel reports, ingest CSVs, and build interactive dashboards."
    elif preset == "Building MCP Servers in Python":
        default_skill = "Model Context Protocol (MCP)"
        default_level = "Intermediate"
        default_duration = 10
        default_hours = 2.5
        default_goal = "Create custom MCP tools and connect them to Claude Desktop and Antigravity."
    elif preset == "Full-Stack React & Node.js":
        default_skill = "Modern Full-Stack Web Development"
        default_level = "Intermediate"
        default_duration = 30
        default_hours = 3.0
        default_goal = "Ship a portfolio web app with user authentication and database persistence."
    elif preset == "Prompt Engineering & LLM Apps":
        default_skill = "Prompt Engineering & Generative AI"
        default_level = "Beginner"
        default_duration = 7
        default_hours = 1.5
        default_goal = "Master few-shot prompting, structured JSON outputs, and LLM reasoning."
    elif preset == "Machine Learning Fundamentals":
        default_skill = "Machine Learning with Scikit-Learn"
        default_level = "Intermediate"
        default_duration = 21
        default_hours = 2.5
        default_goal = "Train predictive models, perform feature engineering, and deploy via Streamlit."

    # ---------------------------------------------------------
    # Main Header & Hero Banner
    # ---------------------------------------------------------
    st.markdown(
        """
        <div class="hero-container">
            <h1 class="hero-title">
                <span>🎓</span> AI Learning Path Generator
            </h1>
            <p class="hero-subtitle">
                Transform any skill or career ambition into a structured, daily learning roadmap. 
                Get personalized learning objectives, weekly milestones, hands-on exercises, 
                and a portfolio-ready capstone project idea in seconds.
            </p>
            <div class="hero-badges">
                <span class="hero-badge">⚡ Powered by Gemini AI</span>
                <span class="hero-badge">🛠️ Official Model Context Protocol (MCP) Server</span>
                <span class="hero-badge">📅 Week-by-Week Milestones</span>
                <span class="hero-badge">🏆 Capstone Project Included</span>
                <span class="hero-badge">💾 Downloadable Markdown</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # ---------------------------------------------------------
    # Input Form
    # ---------------------------------------------------------
    st.subheader("📋 Enter Your Learning Profile")
    st.markdown("Customize your preferences below to tailor the roadmap to your exact schedule and goals.")

    with st.form("learning_path_form", clear_on_submit=False):
        col1, col2 = st.columns(2)

        with col1:
            student_name = st.text_input(
                "👤 Student Name",
                value=default_name,
                placeholder="e.g. Alex Johnson",
                help="Your name or the learner's name."
            )
            
            skill = st.text_input(
                "🎯 Skill to Learn",
                value=default_skill,
                placeholder="e.g., Python, Docker, MCP Servers, Machine Learning",
                help="The specific technology, subject, or domain you want to master."
            )

            level_options = ["Beginner", "Intermediate", "Advanced"]
            level_index = level_options.index(default_level) if default_level in level_options else 0
            current_level = st.radio(
                "📊 Current Experience Level",
                options=level_options,
                index=level_index,
                horizontal=True,
                help="Your current familiarity with this topic."
            )

        with col2:
            duration_days = st.number_input(
                "⏳ Learning Duration (in Days)",
                min_value=3,
                max_value=180,
                value=default_duration,
                step=1,
                help="How many total days you plan to dedicate to this roadmap."
            )

            daily_hours = st.slider(
                "⏰ Daily Study Commitment (Hours/Day)",
                min_value=0.5,
                max_value=10.0,
                value=float(default_hours),
                step=0.5,
                help="Realistic amount of focused hours you can invest each day."
            )

            learning_goal = st.text_area(
                "🎯 Primary Learning Goal",
                value=default_goal,
                placeholder="e.g., Build an MCP server, crack technical interviews, build a production web app",
                height=85,
                help="What concrete accomplishment or milestone do you want to achieve?"
            )

        # Form Submit Button
        submitted = st.form_submit_button(
            "🚀 Generate My Learning Path",
            use_container_width=True,
            type="primary"
        )

    # ---------------------------------------------------------
    # Generation & Display Logic
    # ---------------------------------------------------------
    # Use session state to persist generated results across UI reruns
    if "roadmap_content" not in st.session_state:
        st.session_state.roadmap_content = None
    if "is_demo" not in st.session_state:
        st.session_state.is_demo = True
    if "meta_info" not in st.session_state:
        st.session_state.meta_info = {}

    if submitted:
        # Validate inputs
        if not skill.strip():
            st.error("Please enter a skill you want to learn!")
            return
            
        with st.spinner("🤖 Consulting AI Curriculum Architect... Crafting your personalized roadmap..."):
            roadmap_md, is_demo, error_note = generate_learning_roadmap(
                student_name=student_name,
                skill=skill,
                level=current_level,
                duration_days=int(duration_days),
                daily_hours=float(daily_hours),
                learning_goal=learning_goal,
                api_key=user_api_key,
                model_name=selected_model
            )

        st.session_state.roadmap_content = roadmap_md
        st.session_state.is_demo = is_demo
        st.session_state.meta_info = {
            "student_name": student_name,
            "skill": skill,
            "level": current_level,
            "duration_days": duration_days,
            "daily_hours": daily_hours,
            "total_hours": round(duration_days * daily_hours, 1),
            "goal": learning_goal,
            "error_note": error_note,
            "model_used": selected_model
        }

    # ---------------------------------------------------------
    # Render Roadmap if Available
    # ---------------------------------------------------------
    if st.session_state.roadmap_content:
        meta = st.session_state.meta_info
        
        st.markdown("---")
        
        # Status Notification
        if st.session_state.is_demo:
            if meta.get("error_note"):
                st.warning(f"⚠️ {meta['error_note']}")
            else:
                st.info(
                    "💡 **Smart Demo Mode:** Running with tailored offline curriculum. "
                    "To generate dynamic responses with live AI, enter your Gemini API Key in the left sidebar."
                )
        else:
            st.success(f"✨ Roadmap successfully generated using Google Gemini AI (`{meta.get('model_used', 'gemini-3.8-flash')}`)!")

        # High-level Metrics Dashboard
        col_m1, col_m2, col_m3, col_m4 = st.columns(4)
        with col_m1:
            st.markdown(
                f"""
                <div class="metric-card">
                    <div class="metric-value">{meta.get('duration_days', 0)}</div>
                    <div class="metric-label">Total Days</div>
                </div>
                """,
                unsafe_allow_html=True
            )
        with col_m2:
            st.markdown(
                f"""
                <div class="metric-card">
                    <div class="metric-value">{meta.get('daily_hours', 0)}h</div>
                    <div class="metric-label">Daily Study</div>
                </div>
                """,
                unsafe_allow_html=True
            )
        with col_m3:
            st.markdown(
                f"""
                <div class="metric-card">
                    <div class="metric-value">{meta.get('total_hours', 0)}h</div>
                    <div class="metric-label">Total Investment</div>
                </div>
                """,
                unsafe_allow_html=True
            )
        with col_m4:
            st.markdown(
                f"""
                <div class="metric-card">
                    <div class="metric-value">{meta.get('level', 'Beginner')}</div>
                    <div class="metric-label">Target Level</div>
                </div>
                """,
                unsafe_allow_html=True
            )

        st.markdown("<br>", unsafe_allow_html=True)

        # Tabbed Views: Interactive Roadmap, Study Checklist, MCP Server, and Export
        tab1, tab2, tab3, tab4 = st.tabs([
            "📖 Full Roadmap",
            "✅ Interactive Checklist",
            "🛠️ Model Context Protocol (MCP)",
            "📥 Export & Download"
        ])

        with tab1:
            st.markdown(st.session_state.roadmap_content)

        with tab2:
            st.markdown("### 🎯 Your Learning Milestone Tracker")
            st.markdown("Check off items as you complete them during your study journey:")
            
            # Interactive checkboxes for student engagement
            weeks_count = max(1, round(meta.get("duration_days", 14) / 7))
            st.checkbox("Orientation: Workspace Setup, Git Repository & Tools", key="chk_0")
            for w in range(1, weeks_count + 1):
                st.checkbox(f"Week {w} Study Modules & Daily Practice Drills", key=f"chk_w{w}")
            st.checkbox("Hands-on Practice Exercises Completed", key="chk_ex")
            st.checkbox("Capstone Mini-Project MVP Implemented", key="chk_proj_mvp")
            st.checkbox("Capstone Project Tested, Documented & Shared", key="chk_proj_done")
            st.checkbox("Next Steps & Career Plan Outlined", key="chk_next")

        with tab3:
            st.markdown("### 🛠️ Model Context Protocol (MCP) Integration")
            st.markdown(
                """
                This project includes an **official Model Context Protocol (MCP) Server** (`mcp_server.py`) 
                built with the official Python MCP SDK (`mcp`). AI agents (such as Claude Desktop, Antigravity, 
                or Cursor) can connect to this server over standard I/O (stdio) to dynamically invoke learning tools.
                """
            )
            
            st.markdown("#### 🧰 Registered MCP Tools:")
            col_t1, col_t2, col_t3 = st.columns(3)
            with col_t1:
                st.info(
                    "**1. `generate_learning_plan`**\n\n"
                    "Generates a complete, tailored learning roadmap for any skill with objectives, schedule, and projects."
                )
            with col_t2:
                st.info(
                    "**2. `get_learning_resources`**\n\n"
                    "Returns vetted, high-value documentation, official tutorials, and GitHub repositories."
                )
            with col_t3:
                st.info(
                    "**3. `create_daily_study_schedule`**\n\n"
                    "Calculates Pomodoro blocks and day-by-day study sessions based on available hours."
                )

            st.markdown("#### 🧪 Test MCP Tools Directly:")
            col_b1, col_b2 = st.columns(2)
            with col_b1:
                if st.button("📚 Run MCP: Fetch Learning Resources", use_container_width=True):
                    res_output = get_learning_resources_data(
                        skill=meta.get("skill", "Python"),
                        level=meta.get("level", "Beginner")
                    )
                    st.markdown(res_output)
            with col_b2:
                if st.button("⏰ Run MCP: Generate Daily Study Schedule", use_container_width=True):
                    sched_output = create_study_schedule_data(
                        skill=meta.get("skill", "Python"),
                        duration_days=meta.get("duration_days", 7),
                        daily_hours=meta.get("daily_hours", 2.0)
                    )
                    st.markdown(sched_output)

            st.markdown("---")
            st.markdown("#### 🔌 Connect to Claude Desktop or Antigravity:")
            st.write("Add this configuration block to your `claude_desktop_config.json`:")
            
            # Formulate sample JSON config for Windows
            mcp_config = f"""{{
  "mcpServers": {{
    "learning-path-generator": {{
      "command": "c:\\\\Users\\\\sindh\\\\OneDrive\\\\Desktop\\\\AI-Learning-Path-Generator\\\\.venv\\\\Scripts\\\\python.exe",
      "args": [
        "c:\\\\Users\\\\sindh\\\\OneDrive\\\\Desktop\\\\AI-Learning-Path-Generator\\\\mcp_server.py"
      ],
      "env": {{
        "GEMINI_API_KEY": "YOUR_GEMINI_API_KEY_HERE"
      }}
    }}
  }}
}}"""
            st.code(mcp_config, language="json")

        with tab4:
            st.markdown("### 📥 Download Your Roadmap")
            st.write("Save your customized curriculum locally to review offline or share with mentors.")

            file_prefix = meta.get("skill", "learning_roadmap").replace(" ", "_").lower()
            download_filename = f"{file_prefix}_roadmap.md"

            col_d1, col_d2 = st.columns([1, 2])
            with col_d1:
                st.download_button(
                    label="📄 Download Markdown File (.md)",
                    data=st.session_state.roadmap_content,
                    file_name=download_filename,
                    mime="text/markdown",
                    type="primary"
                )

            st.markdown("#### 📋 Raw Markdown Code")
            st.code(st.session_state.roadmap_content, language="markdown")


if __name__ == "__main__":
    main()
