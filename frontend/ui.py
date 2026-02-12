import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import time

# --- CONFIGURATION ---
# CHANGE THIS TO YOUR RENDER URL AFTER DEPLOYMENT
API_URL = "https://aionyx-mayank.onrender.com/api/v1"

st.set_page_config(
    page_title="AIONYX | Mayank Vispute",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- PROFESSIONAL STYLING ---
st.markdown("""
    <style>
    /* MAIN THEME */
    .stApp {
        background: linear-gradient(to bottom right, #ffffff, #f8f9fa);
        color: #2c3e50;
    }
    
    /* DEVELOPER BADGE */
    .dev-badge {
        font-size: 12px;
        color: #7f8c8d;
        text-align: center;
        padding: 10px;
        border-top: 1px solid #eee;
        margin-top: 20px;
    }

    /* ANIMATIONS */
    @keyframes fadeUp {
        from { opacity: 0; transform: translateY(15px); }
        to { opacity: 1; transform: translateY(0); }
    }

    /* GLASS CARDS */
    .glass-card {
        background: rgba(255, 255, 255, 0.9);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(231, 235, 240, 0.8);
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
        margin-bottom: 15px;
        animation: fadeUp 0.5s ease-out;
    }
    
    /* CHAT BUBBLES */
    .chat-bubble {
        padding: 12px 16px;
        border-radius: 10px;
        margin-bottom: 8px;
        max-width: 80%;
        font-size: 0.95rem;
    }
    .user-msg {
        background-color: #e3f2fd;
        border-left: 4px solid #2196f3;
        margin-left: auto;
    }
    .ai-msg {
        background-color: #f5f5f5;
        border-left: 4px solid #4caf50;
    }
    </style>
""", unsafe_allow_html=True)

# --- SIDEBAR WITH CREDITS ---
with st.sidebar:
    st.header("AIONYX Control")
    uploaded_file = st.file_uploader("Upload CSV", type=["csv"])
    
    st.markdown("---")
    if uploaded_file:
        st.success("✅ System Online")
    else:
        st.info("Waiting for Data...")
        
    # --- YOUR BRANDING ---
    st.markdown("---")
    st.markdown("""
        <div class="dev-badge">
            <b>Developed by Mayank Vispute</b><br>
            © 2026 AIONYX Systems<br>
            All Rights Reserved.
        </div>
    """, unsafe_allow_html=True)

# --- MAIN HEADER ---
col1, col2 = st.columns([3, 1])
with col1:
    st.title("🧬 AIONYX Intelligence")
    st.markdown("**Architected by Mayank Vispute** | Enterprise Data Solution")

# --- LOGIC ---
if "messages" not in st.session_state:
    st.session_state.messages = []

if uploaded_file is not None:
    uploaded_file.seek(0)
    df = pd.read_csv(uploaded_file)
    uploaded_file.seek(0)

    # API CALL
    if "analysis_data" not in st.session_state or st.session_state.get("current_file") != uploaded_file.name:
        with st.spinner("Mayank's AI Engine is processing..."):
            try:
                files = {"file": (uploaded_file.name, uploaded_file, "text/csv")}
                response = requests.post(f"{API_URL}/analyze", files=files)
                if response.status_code == 200:
                    st.session_state.analysis_data = response.json()
                    st.session_state.current_file = uploaded_file.name
                else:
                    st.error(f"Error: {response.text}")
            except Exception as e:
                st.error(f"Connection Failed: {e}")

    data = st.session_state.get("analysis_data")
    if data:
        summary = data["summary"]
        
        # METRICS
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Total Rows", summary["total_rows"])
        c2.metric("Columns", summary["total_columns"])
        c3.metric("Duplicates", summary["duplicate_rows"])
        c4.metric("Memory", f"{summary['memory_usage_kb']} KB")
        
        # TABS
        t1, t2, t3, t4 = st.tabs(["📋 Executive Brief", "📈 Analytics", "💬 AI Chat", "📄 Raw Data"])
        
        with t1:
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            st.markdown("### AI Executive Summary")
            st.write(data.get("ai_analysis", "Processing..."))
            st.markdown('</div>', unsafe_allow_html=True)
            
        with t2:
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            num_cols = df.select_dtypes(include=['number']).columns
            if len(num_cols) > 0:
                sel = st.selectbox("Select Metric", num_cols)
                st.plotly_chart(px.line(df, y=sel, title=f"Trend: {sel}"), use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
            
        with t3:
            st.markdown("### Ask the Data")
            for msg in st.session_state.messages:
                c = "user-msg" if msg["role"] == "user" else "ai-msg"
                st.markdown(f'<div class="chat-bubble {c}">{msg["content"]}</div>', unsafe_allow_html=True)
            
            if prompt := st.chat_input("Query System..."):
                st.session_state.messages.append({"role": "user", "content": prompt})
                st.markdown(f'<div class="chat-bubble user-msg">{prompt}</div>', unsafe_allow_html=True)
                
                # CHAT LOGIC
                try:
                    res = requests.post(f"{API_URL}/chat", json={"question": prompt, "profile": data})
                    ans = res.json()["answer"]
                    st.session_state.messages.append({"role": "assistant", "content": ans})
                    st.markdown(f'<div class="chat-bubble ai-msg">{ans}</div>', unsafe_allow_html=True)
                except:
                    st.error("AI Error")

        with t4:
            st.dataframe(df)
else:
    st.info("Upload data to initialize System.")


