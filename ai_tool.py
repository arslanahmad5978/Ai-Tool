import streamlit as st
import requests
from datetime import datetime, timedelta

# ---------- PAGE CONFIG ----------
st.set_page_config(page_title="YouTube Viral Topics Tool", page_icon="🎥", layout="wide")

# ---------- CUSTOM CSS ----------
st.markdown("""
    <style>
        body {
            background: linear-gradient(135deg, #121212, #1e1e1e);
            color: #fff;
        }
        .main-title {
            text-align: center;
            font-size: 48px;
            font-weight: 800;
            color: #ff4b4b;
            margin-bottom: 10px;
            text-shadow: 0 0 20px rgba(255,75,75,0.5);
        }
        .sub-text {
            text-align: center;
            color: #ddd;
            font-size: 18px;
            margin-bottom: 40px;
        }
        .stButton>button {
            background: linear-gradient(90deg, #ff4b4b, #ff6b81);
            color: white;
            font-weight: 600;
            border: none;
            border-radius: 12px;
            padding: 10px 25px;
            transition: 0.3s;
        }
        .stButton>button:hover {
            background: linear-gradient(90deg, #ff6b81, #ff4b4b);
            transform: scale(1.05);
        }
        .card {
            background: rgba(255, 255, 255, 0.06);
            border-radius: 16px;
            padding: 18px;
            margin: 10px 0;
            backdrop-filter: blur(15px);
            border: 1px solid rgba(255,255,255,0.1);
            box-shadow: 0 4px 20px rgba(0,0,0,0.2);
        }
        .result-box {
            background: rgba(255,255,255,0.08);
            padding: 20px;
            border-radius: 14px;
            margin-bottom: 15px;
            border: 1px solid rgba(255,255,255,0.1);
            transition: 0.3s;
        }
        .result-box:hover {
            transform: translateY(-3px);
            box-shadow: 0 6px 25px rgba(255,75,75,0.2);
        }
        .footer {
            text-align: center;
            color: #999;
            margin-top: 50px;
            font-size: 14px;
        }
        textarea, input {
            border-radius: 12px !important;
        }
    </style>
""", unsafe_allow_html=True)

# ---------- HEADER ----------
st.markdown('<h1 class="main-title">🎬 YouTube Viral Topics Finder</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-text">Discover trending videos from small creators — built for growth hackers & content explorers 🚀</p>', unsafe_allow_html=True)

# ---------- INPUT FORM ----------
with st.container():
    with st.form("search_form", clear_on_submit=False):
        st.markdown('<div class="card">', unsafe_allow_html=True)

        col1, col2 = st.columns([1, 2])

        with col1:
            days = st.number_input("📅 Days to Search:", min_value=1, max_value=30, value=5)
            creation_filter = st.selectbox(
                "📆 Channel Created After:",
                ["None", "Last 6 Months", "Last 1 Year", "Last 2 Years"]
            )
            max_subs = st.number_input(
                "👤 Max Subscribers:",
                min_value=0,
                max_value=100000,
                value=3000,
                step=500
            )

        with col2:
            user_keywords = st.text_area(
                "🧠 Enter Keywords (comma or newline separated):",
                placeholder="Example:\nReddit Relationship, Cheating Story, Open Marriage"
            )

        col3, col4 = st.columns([1, 1])
        with col3:
            submitted = st.form_submit_button("🚀 Fetch Data")
        with col4:
            if st.form_submit_button("🔄 Refresh Page"):
                st.experimental_rerun()

        st.markdown('</div>', unsafe_allow_html=True)

# ---------- CONVERT INPUT ----------
if user_keywords.strip():
    if "," in user_keywords:
        keywords = [k.strip() for k in user_keywords.split(",") if k.strip()]
    else:
        keywords = [k.strip() for k in user_keywords.split("\n") if k.strip()]
else:
    keywords = []

# ---------- CONSTANTS ----------
API_KEY = "Enter your API Key here"
YOUTUBE_SEARCH_URL = "https://www.googleapis.com/youtube/v3/search"
YOUTUBE_VIDEO_URL = "https://www.googleapis.com/youtube/v3/videos"
YOUTUBE_CHANNEL_URL = "https://www.googleapis.com/youtube/v3/channels"

# ---------- FETCH DATA ----------
if submitted:
    if not API_KEY or API_KEY == "Enter your API Key here":
        st.error("❌ Please add your YouTube API key in the code.")
    elif not keywords:
        st.warning("⚠️ Please enter at least one keyword.")
    else:
        try:
            start_date = (datetime.utcnow() - timedelta(days=int(days))).isoformat("T") + "Z"
            all_results = []

            # Channel creation cutoff logic
            creation_cutoff = None
            if creation_filter != "None":
                today = datetime.utcnow()
                if creation_filter == "Last 6 Months":
                    creation_cutoff = today - timedelta(days=180)
                elif creation_filter == "Last 1 Year":
                    creation_cutoff = today - timedelta(days=365)
                elif creation_filter == "Last 2 Years":
                    creation_cutoff = today - timedelta(days=730)
