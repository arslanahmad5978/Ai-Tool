import streamlit as st
import requests
from datetime import datetime, timedelta

# ---------- PAGE CONFIG ----------
st.set_page_config(page_title="YouTube Viral Topics Tool", layout="wide")

# ---------- CUSTOM STYLES ----------
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
        .video-card {
            background: rgba(255, 255, 255, 0.06);
            border-radius: 16px;
            padding: 15px;
            margin-bottom: 20px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.3);
            transition: 0.3s;
        }
        .video-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 6px 25px rgba(255,75,75,0.3);
        }
        iframe {
            border-radius: 12px;
        }
    </style>
""", unsafe_allow_html=True)

# ---------- HEADER ----------
st.markdown('<h1 class="main-title">🎬 YouTube Viral Topics Finder</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-text">Find viral videos from small creators 🚀</p>', unsafe_allow_html=True)

# ---------- INPUT FORM ----------
with st.container():
    with st.form("search_form"):
        user_keywords = st.text_area("🧠 Enter Keywords (comma or newline separated):", "cheatingstory, funny, cat")
        days = st.number_input("📅 Days to Search:", 1, 30, 5)
        max_subs = st.number_input("👤 Max Subscribers:", 0, 100000, 3000, step=500)

        col1, col2 = st.columns([1, 1])
        with col1:
            submitted = st.form_submit_button("🚀 Fetch Data")
        with col2:
            refresh = st.form_submit_button("🔁 Refresh Page")

        if refresh:
            st.rerun()

# ---------- CONSTANTS ----------
API_KEY = "AIzaSyDpg5IspCa_V23iiY0c9w7yI3nB-IYdIDQ"
YOUTUBE_SEARCH_URL = "https://www.googleapis.com/youtube/v3/search"
YOUTUBE_VIDEO_URL = "https://www.googleapis.com/youtube/v3/videos"
YOUTUBE_CHANNEL_URL = "https://www.googleapis.com/youtube/v3/channels"

# ---------- FETCH DATA ----------
if submitted:
    if not user_keywords.strip():
        st.warning("⚠️ Please enter at least one keyword.")
    else:
        keywords = [x.strip() for x in user_keywords.replace("\n", ",").split(",") if x.strip()]
        start_date = (datetime.utcnow() - timedelta(days=int(days))).isoformat("T") + "Z"
        all_results = []

        for keyword in keywords:
            st.markdown(f"🔍 Searching: <b>{keyword}</b>", unsafe_allow_html=True)

            search_params = {
                "part": "snippet",
                "q": keyword,
                "type": "video",
                "order": "viewCount",
                "publishedAfter": start_date,
                "maxResults": 6,
                "key": API_KEY,
            }

            data = requests.get(YOUTUBE_SEARCH_URL, params=search_params).json()
            videos = data.get("items", [])
            if not videos:
                continue

            video_ids = [v["id"]["videoId"] for v in videos if "videoId" in v["id"]]
            channel_ids = [v["snippet"]["channelId"] for v in videos if "snippet" in v]

            stats_data = requests.get(
                YOUTUBE_VIDEO_URL,
                params={"part": "statistics", "id": ",".join(video_ids), "key": API_KEY}
            ).json()

            channel_data = requests.get(
                YOUTUBE_CHANNEL_URL,
                params={"part": "statistics", "id": ",".join(channel_ids), "key": API_KEY}
            ).json()

            for video, vstat, cstat in zip(videos, stats_data.get("items", []), channel_data.get("items", [])):
                snippet = video.get("snippet", {})
                statistics = vstat.get("statistics", {})
                channel_stats = cstat.get("statistics", {})

                title = snippet.get("title", "Untitled Video")
                description = snippet.get("description", "No description")[:120]
                views = int(statistics.get("viewCount", 0))
                subs = int(channel_stats.get("subscriberCount", 0))

                if subs < max_subs:
                    all_results.append({
                        "VideoID": video["id"]["videoId"],
                        "Title": title,
                        "Description": description,
                        "Views": views,
                        "Subscribers": subs,
                    })

        # ---------- DISPLAY RESULTS ----------
        if all_results:
            st.markdown(f"✅ <b>Found {len(all_results)} viral videos!</b>", unsafe_allow_html=True)

            rows = [all_results[i:i + 3] for i in range(0, len(all_results), 3)]
            for row in rows:
                cols = st.columns(3)
                for col, res in zip(cols, row):
                    with col:
                        st.markdown(f"""
                            <div class="video-card">
                                <iframe width="100%" height="200" src="https://www.youtube.com/embed/{res['VideoID']}" frameborder="0" allowfullscreen></iframe>
                                <h4 style="color:#000;font-weight:800;font-size:20px;margin-top:10px;background-color:#fff;padding:10px;border-radius:10px;text-align:center;">
                                    {res['Title']}
                                </h4>
                                <p style="color:#ccc; font-size:13px;">{res['Description']}</p>
                                <p style="color:#ff6b81; font-size:16px;">👁 {res['Views']:,} views | 👤 {res['Subscribers']:,} subs</p>
                            </div>
                        """, unsafe_allow_html=True)
        else:
            st.warning("😕 No matching small-channel videos found.")
