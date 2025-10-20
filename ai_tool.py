import streamlit as st
import requests
from datetime import datetime, timedelta

# ======================== CONFIG ========================
API_KEY = "AIzaSyDpg5IspCa_V23iiY0c9w7yI3nB-IYdIDQ"  # <-- اپنی API Key یہاں ڈالیں
YOUTUBE_SEARCH_URL = "https://www.googleapis.com/youtube/v3/search"
YOUTUBE_VIDEO_URL = "https://www.googleapis.com/youtube/v3/videos"
YOUTUBE_CHANNEL_URL = "https://www.googleapis.com/youtube/v3/channels"

# ======================== PAGE DESIGN ========================
st.set_page_config(page_title="🎬 YouTube Viral Finder", page_icon="🔥", layout="wide")
st.markdown("""
    <style>
        body {background-color: #0e1117; color: white;}
        .main-title {text-align: center; color: #ff4b4b; font-size: 38px; font-weight: bold; padding-bottom: 10px;}
        .sub-title {text-align: center; color: #bbb; font-size: 18px; margin-bottom: 30px;}
        .result-box {background-color: #1e242e; padding: 15px; border-radius: 10px; margin-bottom: 15px; box-shadow: 0 0 10px rgba(255,75,75,0.2);}
        .result-box:hover {background-color: #2c303a;}
        a {text-decoration: none;}
    </style>
""", unsafe_allow_html=True)

# ======================== HEADER ========================
st.markdown("<h1 class='main-title'>🎥 YouTube Viral Topics Finder</h1>", unsafe_allow_html=True)
st.markdown("<p class='sub-title'>Find trending small-channel videos fast!</p>", unsafe_allow_html=True)

# ======================== INPUT FORM ========================
with st.form("input_form"):
    col1, col2 = st.columns([1, 1])
    with col1:
        days = st.number_input("📅 Enter Days to Search (1–30):", min_value=1, max_value=30, value=5)
    with col2:
        max_subs = st.number_input("👤 Max Subscribers:", min_value=0, max_value=100000, value=3000, step=500)

    creation_filter = st.selectbox(
        "📆 Channel Creation Date Filter:",
        ["None", "Last 6 Months", "Last 1 Year", "Last 2 Years"]
    )

    keywords_input = st.text_area(
        "🧠 Enter Keywords (comma or new-line separated):",
        placeholder="e.g. Reddit Relationship, Cheating Story, AITA Update"
    )

    col_a, col_b = st.columns([1, 1])
    with col_a:
        submit = st.form_submit_button("🚀 Fetch Data")
    with col_b:
        refresh = st.form_submit_button("🔄 Refresh Page")

# Safe refresh
if refresh:
    st.rerun()

# ======================== MAIN LOGIC ========================
if submit:
    if not API_KEY or API_KEY == "Enter your API Key here":
        st.error("❌ Please enter your valid YouTube API key in the code.")
    elif not keywords_input.strip():
        st.warning("⚠️ Please enter at least one keyword.")
    else:
        try:
            # prepare keywords list
            keywords = [k.strip() for k in keywords_input.replace("\n", ",").split(",") if k.strip()]
            start_date = (datetime.utcnow() - timedelta(days=int(days))).isoformat("T") + "Z"
            all_results = []

            # Channel creation cutoff logic
            creation_cutoff_
