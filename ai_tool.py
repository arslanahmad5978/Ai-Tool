import streamlit as st
import requests
from datetime import datetime, timedelta

# YouTube API Key
API_KEY = "AIzaSyDpg5IspCa_V23iiY0c9w7yI3nB-IYdIDQ"
YOUTUBE_SEARCH_URL = "https://www.googleapis.com/youtube/v3/search"
YOUTUBE_VIDEO_URL = "https://www.googleapis.com/youtube/v3/videos"
YOUTUBE_CHANNEL_URL = "https://www.googleapis.com/youtube/v3/channels"

# Streamlit App Title
st.title("🎥 YouTube Viral Topics Tool")

# Input Fields
days = st.number_input("Enter Days to Search (1-30):", min_value=1, max_value=30, value=5)

# New: User Keyword Input
user_keywords = st.text_area(
    "Enter Keywords (separate with commas or new lines):",
    placeholder="Example:\nReddit Relationship, Cheating Story, Open Marriage"
)

# Convert input text to a list of keywords
if user_keywords.strip():
    if "," in user_keywords:
        keywords = [k.strip() for k in user_keywords.split(",") if k.strip()]
    else:
        keywords = [k.strip() for k in user_keywords.split("\n") if k.strip()]
else:
    keywords = []

# Fetch Data Button
if st.button("Fetch Data"):
    if not API_KEY or API_KEY == "Enter your API Key here":
        st.error("❌ Please enter your valid YouTube API key in the code.")
    elif not keywords:
        st.warning("⚠️ Please enter at least one keyword.")
    else:
        try:
            # Calculate date range
            start_date = (datetime.utcnow() - timedelta(days=int(days))).isoformat("T") + "Z"
            all_results = []

            # Iterate over the list of keywords
            for keyword in keywords:
                st.write(f"🔍 Searching for keyword: **{keyword}**")

                search_params = {
                    "part": "snippet",
                    "q": keyword,
                    "type": "video",
                    "order": "viewCount",
                    "publishedAfter": start_date,
                    "maxResults": 5,
                    "key": API_KEY,
                }

                # Fetch video data
                response = requests.get(YOUTUBE_SEARCH_URL, params=search_params)
                data = response.json()

                if "items" not in data or not data["items"]:
                    st.warning(f"No videos found for keyword: {keyword}")
                    continue

                videos = data["items"]
                video_ids = [v["id"]["videoId"] for v in videos if "id" in v and "videoId" in v["id"]]
                channel_ids = [v["snippet"]["channelId"] for v in videos if "snippet" in v and "channelId" in v["snippet"]]

                if not video_ids or not channel_ids:
                    st.warning(f"Skipping keyword: {keyword} due to missing video/channel data.")
                    continue

                # Fetch video statistics
                stats_params = {"part": "statistics", "id": ",".join(video_ids), "key": API_KEY}
                stats_response = requests.get(YOUTUBE_VIDEO_URL, params=stats_params)
                stats_data = stats_response.json()

                # Fetch channel statistics
                channel_params = {"part": "statistics", "id": ",".join(channel_ids), "key": API_KEY}
                channel_response = requests.get(YOUTUBE_CHANNEL_URL, params=channel_params)
                channel_data = channel_response.json()

                if "items" not in stats_data or "items" not in channel_data:
                    st.warning(f"Failed to fetch stats for keyword: {keyword}")
                    continue

                stats = stats_data["items"]
                channels = channel_data["items"]

                # Collect results
                for video, stat, channel in zip(videos, stats, channels):
                    title = video["snippet"].get("title", "N/A")
                    description = video["snippet"].get("description", "")[:200]
                    video_url = f"https://www.youtube.com/watch?v={video['id']['videoId']}"
                    views = int(stat["statistics"].get("viewCount", 0))
                    subs = int(channel["statistics"].get("subscriberCount", 0))

                    if subs < 3000:  # Only include small channels
                        all_results.append({
                            "Title": title,
                            "Description": description,
                            "URL": video_url,
                            "Views": views,
                            "Subscribers": subs
                        })

            # Display results
            if all_results:
                st.success(f"✅ Found {len(all_results)} results across all keywords!")
                for result in all_results:
                    st.markdown(
                        f"**🎬 Title:** {result['Title']}  \n"
                        f"**📝 Description:** {result['Description']}  \n"
                        f"**🔗 URL:** [Watch Video]({result['URL']})  \n"
                        f"**👁 Views:** {result['Views']}  \n"
                        f"**👤 Subscribers:** {result['Subscribers']}"
                    )
                    st.write("---")
            else:
                st.warning("No results found for small channels (under 3K subs).")

        except Exception as e:
            st.error(f"An error occurred: {e}")
