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
    </style>
""", unsafe_allow_html=True)

# ---------- HEADER ----------
st.markdown('<h1 class="main-title">🎬 YouTube Viral Topics Finder</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-text">Discover trending videos from small creators 🚀</p>', unsafe_allow_html=True)

# ---------- INPUT FORM ----------
with st.form("search_form", clear_on_submit=False):
    st.markdown('<div style="background:rgba(255,255,255,0.05);padding:20px;border-radius:16px;">', unsafe_allow_html=True)
    col1, col2 = st.columns([1, 1])
    with col1:
        days = st.number_input("📅 Days to Search:", min_value=1, max_value=30, value=5)
    with col2:
        max_subs = st.number_input("👤 Max Subscribers:", min_value=0, max_value=100000, value=3000, step=500)

    creation_filter = st.selectbox(
        "📆 Channel Creation Date Filter:",
        ["None", "Last 6 Months", "Last 1 Year", "Last 2 Years"]
    )

    user_keywords = st.text_area(
        "🧠 Enter Keywords (comma or newline separated):",
        placeholder="Example:\nReddit Relationship, Cheating Story, Open Marriage"
    )

    col3, col4 = st.columns([1, 1])
    with col3:
        submitted = st.form_submit_button("🚀 Fetch Data")
    with col4:
        refresh = st.form_submit_button("🔄 Refresh Page")
    st.markdown('</div>', unsafe_allow_html=True)

if refresh:
    st.rerun()

# ---------- API CONSTANTS ----------
API_KEY = "Enter your API Key here"
YOUTUBE_SEARCH_URL = "https://www.googleapis.com/youtube/v3/search"
YOUTUBE_VIDEO_URL = "https://www.googleapis.com/youtube/v3/videos"
YOUTUBE_CHANNEL_URL = "https://www.googleapis.com/youtube/v3/channels"

# ---------- MAIN LOGIC ----------
if submitted:
    if not API_KEY or API_KEY == "AIzaSyDpg5IspCa_V23iiY0c9w7yI3nB-IYdIDQ":
        st.error("❌ Please add your YouTube API key in the code.")
    elif not user_keywords.strip():
        st.warning("⚠️ Please enter at least one keyword.")
    else:
        try:
            # Prepare keywords list
            if "," in user_keywords:
                keywords = [k.strip() for k in user_keywords.split(",") if k.strip()]
            else:
                keywords = [k.strip() for k in user_keywords.split("\n") if k.strip()]

            start_date = (datetime.utcnow() - timedelta(days=int(days))).isoformat("T") + "Z"
            all_results = []

            # Channel creation cutoff logic
            creation_cutoff = None
            today = datetime.utcnow()
            if creation_filter == "Last 6 Months":
                creation_cutoff = today - timedelta(days=180)
            elif creation_filter == "Last 1 Year":
                creation_cutoff = today - timedelta(days=365)
            elif creation_filter == "Last 2 Years":
                creation_cutoff = today - timedelta(days=730)

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

                # Get stats
                stats_data = requests.get(YOUTUBE_VIDEO_URL, params={"part": "statistics", "id": ",".join(video_ids), "key": API_KEY}).json()
                channel_data = requests.get(YOUTUBE_CHANNEL_URL, params={"part": "snippet,statistics", "id": ",".join(channel_ids), "key": API_KEY}).json()

                if "items" not in stats_data or "items" not in channel_data:
                    continue

                for video, stat, channel in zip(videos, stats_data["items"], channel_data["items"]):
                    title = video["snippet"].get("title", "N/A")
                    desc = video["snippet"].get("description", "")[:180]
                    video_url = f"https://www.youtube.com/watch?v={video['id']['videoId']}"
                    views = int(stat["statistics"].get("viewCount", 0))
                    subs = int(channel["statistics"].get("subscriberCount", 0))
                    creation_date = channel["snippet"].get("publishedAt", "")

                    # Filter channel creation date
                    if creation_cutoff and creation_date:
                        try:
                            channel_date = datetime.fromisoformat(creation_date.replace("Z", ""))
                            if channel_date < creation_cutoff:
                                continue
                        except:
                            pass

                    # Filter subscriber count
                    if subs > max_subs:
                        continue

                    all_results.append({
                        "Title": title,
                        "Description": desc,
                        "URL": video_url,
                        "Views": views,
                        "Subscribers": subs,
                        "Channel_Created": creation_date[:10] if creation_date else "Unknown"
                    })

            progress.empty()

            # ---------- DISPLAY RESULTS ----------
            if all_results:
                st.markdown(f"<h3 style='color:#ff4b4b;'>✅ Found {len(all_results)} viral videos!</h3>", unsafe_allow_html=True)
                for res in all_results:
                    st.markdown(f"""
                        <div class="result-box">
                            <b>🎬 Title:</b> {res['Title']}<br>
                            <b>📝 Description:</b> {res['Description']}<br>
                            <b>🔗 Link:</b> <a href="{res['URL']}" target="_blank" style="color:#ff6b81;">Watch Video</a><br>
                            <b>👁 Views:</b> {res['Views']}<br>
                            <b>👤 Subscribers:</b> {res['Subscribers']}<br>
                            <b>📆 Channel Created:</b> {res['Channel_Created']}
                        </div>
                    """, unsafe_allow_html=True)
            else:
                st.warning("😕 No matching small-channel videos found.")

        except Exception as e:
            st.error(f"An error occurred: {e}")

# ---------- FOOTER ----------
st.markdown('<p class="footer">⚡ Built with ❤️ by <b>Sir Hassan & Ustad ka Shagird</b></p>', unsafe_allow_html=True)
