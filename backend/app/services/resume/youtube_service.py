# app/youtube_service.py

import requests
from app.services.resume.config import YOUTUBE_API_KEY


def fetch_youtube_links(skill, max_results=3):

    url = "https://www.googleapis.com/youtube/v3/search"

    params = {
        "part": "snippet",
        "q": f"{skill} full course tutorial",
        "key": YOUTUBE_API_KEY,
        "maxResults": max_results,
        "type": "video"
    }

    response = requests.get(url, params=params)
    data = response.json()

    videos = []

    for item in data.get("items", [])[:max_results]:

        video_id = item["id"]["videoId"]
        snippet = item["snippet"]

        videos.append({
            "title": snippet["title"],
            "thumbnail": snippet["thumbnails"]["medium"]["url"],
            "channel": snippet["channelTitle"],
            "url": f"https://www.youtube.com/watch?v={video_id}"
        })

    return videos
