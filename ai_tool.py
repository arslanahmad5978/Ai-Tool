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
        .footer {
            text-align: center;
            color: #999;
            margin-top: 50px;
            font-size: 14px;
        }
        .video-grid {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 20px;
        }
        .video-card {
            background: rgba(255, 255, 255, 0.06);
            border-radius: 16px;
            padding: 15px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.3);
            transition: 0.3s;
        }
        .video-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 6px 25px rgba(255,75,75,0.3);
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
        with col2:
            user_keywords = st.text_area(
                "🧠 Enter Keywords (comma or newline separated):",
                placeholder="Example:\nReddit Relationship, Cheating Story, Open Marriage"
            )

        # Subscriber limit input
        max_subs = st.number_input(
            "👤 Max Subscribers to Include:",
            min_value=0,
            max_value=100000,
            value=3000,
            step=500
        )

        col3, col4 = st.columns([1, 1])
        with col3:
            submitted = st.form_submit_button("🚀 Fetch Data")
        with col4:
            refresh = st.form_submit_button("🔄 Refresh Page")

        if refresh:
            st.rerun()

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
API_KEY = "AIzaSyDpg5IspCa_V23iiY0c9w7yI3nB-IYdIDQ"
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
            progress = st.progress(0)
            total = len(keywords)

            for i, keyword in enumerate(keywords, start=1):
                st.markdown(f"<p style='color:#ff6b81;'>🔍 Searching: <b>{keyword}</b> ({i}/{total})</p>", unsafe_allow_html=True)
                progress.progress(i / total)

                search_params = {
                    "part": "snippet",
                    "q": keyword,
                    "type": "video",
                    "order": "viewCount",
                    "publishedAfter": start_date,
                    "maxResults": 5,
                    "key": API_KEY,
                }

                response = requests.get(YOUTUBE_SEARCH_URL, params=search_params)
                data = response.json()

                if "items" not in data or not data["items"]:
                    continue

                videos = data["items"]
                video_ids = [v["id"]["videoId"] for v in videos if "id" in v and "videoId" in v["id"]]
                channel_ids = [v["snippet"]["channelId"] for v in videos if "snippet" in v and "channelId" in v["snippet"]]

                if not video_ids or not channel_ids:
                    continue

                # Get video + channel stats
                stats_data = requests.get(
                    YOUTUBE_VIDEO_URL,
                    params={"part": "statistics", "id": ",".join(video_ids), "key": API_KEY}
                ).json()

                channel_data = requests.get(
                    YOUTUBE_CHANNEL_URL,
                    params={"part": "snippet,statistics", "id": ",".join(channel_ids), "key": API_KEY}
                ).json()

                if "items" not in stats_data or "items" not in channel_data:
                    continue

                for video, stat, channel in zip(videos, stats_data["items"], channel_data["items"]):
                    title = video["snippet"].get("title", "N/A")
                    desc = video["snippet"].get("description", "")[:180]
                    video_id = video["id"]["videoId"]
                    views = int(stat["statistics"].get("viewCount", 0))
                    subs = int(channel["statistics"].get("subscriberCount", 0))

                    # Apply subscriber filter
                    if subs < max_subs:
                        all_results.append({
                            "VideoID": video_id,
                            "Title": title,
                            "Description": desc,
                            "Views": views,
                            "Subscribers": subs
                        })

            progress.empty()

            if all_results:
                st.markdown(f"<h3 style='color:#4caf50;'>✅ Found {len(all_results)} viral videos!</h3>", unsafe_allow_html=True)

                # Build video grid
                grid_html = '<div class="video-grid">'
                for res in all_results:
                    grid_html += f"""
                        <div class="video-card">
                            <iframe width="100%" height="200"
                                    src="https://www.youtube.com/embed/{res['VideoID']}"
                                    frameborder="0" allowfullscreen></iframe>
                            <h4 style="color:#fff; margin-top:10px;">{res['Title']}</h4>
                            <p style="color:#ccc; font-size:13px;">{res['Description']}</p>
                            <p style="color:#ff6b81; font-size:14px;">👁 {res['Views']:,} views | 👤 {res['Subscribers']:,} subs</p>
                        </div>
                    """

                # Fill remaining grid slots with placeholders
                if len(all_results) % 3 != 0:
                    remaining = 3 - (len(all_results) % 3)
                    for _ in range(remaining):
                        grid_html += """
                            <div class="video-card" style="display:flex;align-items:center;justify-content:center;flex-direction:column;">
                                <p style="color:#888;font-size:16px;text-align:center;">🚫 No data available</p>
                            </div>
                        """

                grid_html += "</div>"
                st.components.v1.html(grid_html, height=900, scrolling=True)
            else:
                st.warning("😕 No matching small-channel videos found.")

        except Exception as e:
            st.error(f"An error occurred: {e}")

# ---------- FOOTER ----------
st.markdown('<p class="footer">⚡ Built with ❤️ Sir Hassan | Designed by <b>Ustad ka shagird</b></p>', unsafe_allow_html=True)
