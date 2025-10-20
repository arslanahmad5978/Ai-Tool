import streamlit as st
import requests
from datetime import datetime, timedelta

# ======================== CONFIG ========================
API_KEY = "AIzaSyDpg5IspCa_V23iiY0c9w7yI3nB-IYdIDQ"
YOUTUBE_SEARCH_URL = "https://www.googleapis.com/youtube/v3/search"
YOUTUBE_VIDEO_URL = "https://www.googleapis.com/youtube/v3/videos"
YOUTUBE_CHANNEL_URL = "https://www.googleapis.com/youtube/v3/channels"

# ======================== PAGE DESIGN ========================
st.set_page_config(page_title="🎬 YouTube Viral Finder", page_icon="🔥", layout="wide")

st.markdown("""
    <style>
        body {background-color: #0e1117; color: white;}
        .main-title {
            text-align: center; 
            color: #ff4b4b; 
            font-size: 38px; 
            font-weight: bold;
            padding-bottom: 10px;
        }
        .sub-title {
            text-align: center;
            color: #bbb;
            font-size: 18px;
            margin-bottom: 30px;
        }
        .stTextArea textarea {
            background-color: #1b1f24 !important;
            color: white !important;
        }
        .stNumberInput input {
            background-color: #1b1f24 !important;
            color: white !important;
        }
        .result-box {
            background-color: #1e242e;
            padding: 15px;
            border-radius: 10px;
            margin-bottom: 15px;
            box-shadow: 0 0 10px rgba(255,75,75,0.2);
        }
        .result-box:hover {
            background-color: #2c303a;
        }
        a {text-decoration: none;}
    </style>
""", unsafe_allow_html=True)

# ======================== TITLE ========================
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

    submit = st.form_submit_button("🚀 Fetch Data")
    refresh = st.form_submit_button("🔄 Refresh Page")

if refresh:
    st.experimental_rerun()

# ======================== MAIN LOGIC ========================
if submit:
    try:
        if not keywords_input.strip():
            st.warning("⚠️ Please enter at least one keyword.")
        else:
            keywords = [k.strip() for k in keywords_input.replace("\n", ",").split(",") if k.strip()]
            start_date = (datetime.utcnow() - timedelta(days=int(days))).isoformat("T") + "Z"
            all_results = []

            # Channel creation filter logic
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
                    creation_date = datetime.fromisoformat(channel["snippet"]["publishedAt"].replace("Z", ""))

                    if creation_cutoff and creation_date < creation_cutoff:
                        continue
                    if subs > max_subs:
                        continue

                    all_results.append({
                        "Title": title,
                        "Description": desc,
                        "URL": video_url,
                        "Views": views,
                        "Subscribers": subs,
                        "Created": creation_date.strftime("%Y-%m-%d")
                    })

            progress.empty()

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
                            <b>📆 Channel Created:</b> {res['Created']}
                        </div>
                    """, unsafe_allow_html=True)
            else:
                st.warning("😕 No matching small-channel videos found.")

    except Exception as e:
        st.error(f"❌ Error: {e}")

