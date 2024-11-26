import sys
import os
import json
from googleapiclient.discovery import build
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import TranscriptsDisabled

# Your YouTube API key
api_key = 'AIzaSyBLZYlWDGGfjWSef1eGz5bMsPJzj9jrwJY'

# Get the video ID from the command-line arguments
video_id = sys.argv[1]

# Create 'data' directory if it doesn't exist
os.makedirs('data', exist_ok=True)

youtube = build('youtube', 'v3', developerKey=api_key)

def get_video_metadata(video_id):
    """Retrieve metadata for the given video ID."""
    request = youtube.videos().list(
        part="snippet,contentDetails,statistics",
        id=video_id
    )
    response = request.execute()
    if response["items"]:
        video_info = response["items"][0]
        return {
            "title": video_info["snippet"]["title"],
            "description": video_info["snippet"]["description"],
            "channel_title": video_info["snippet"]["channelTitle"],
            "publish_date": video_info["snippet"]["publishedAt"],
            "view_count": video_info["statistics"].get("viewCount", 0),
            "like_count": video_info["statistics"].get("likeCount", 0),
            "comment_count": video_info["statistics"].get("commentCount", 0),
            "duration": video_info["contentDetails"]["duration"]
        }
    return {"error": "Video metadata not found."}

def get_comments(video_id):
    """Retrieve comments for the given video ID."""
    comments_data = []
    request = youtube.commentThreads().list(
        part="snippet",
        videoId=video_id,
        maxResults=100
    )
    while request:
        response = request.execute()

        for item in response['items']:
            snippet = item['snippet']['topLevelComment']['snippet']
            comment_data = {
                'author': snippet['authorDisplayName'],
                'text': snippet['textDisplay'],
                'likes': snippet['likeCount'],
                'publish_time': snippet['publishedAt'],
                'reply_count': item['snippet']['totalReplyCount']
            }
            comments_data.append(comment_data)

        # Handle pagination
        request = youtube.commentThreads().list_next(request, response)

    return comments_data

def get_transcript(video_id):
    """Retrieve the transcript for the given video ID."""
    try:
        transcript_data = YouTubeTranscriptApi.get_transcript(video_id)
        transcript = []
        for entry in transcript_data:
            transcript.append({
                'text': entry['text'],
                'start_time': entry['start'],
                'duration': entry['duration']
            })
        return transcript
    except TranscriptsDisabled:
        return {"error": "Transcript is disabled for this video."}
    except Exception as e:
        return {"error": str(e)}

# Retrieve data
metadata = get_video_metadata(video_id)
comments = get_comments(video_id)
transcript = get_transcript(video_id)

# Combine data
video_data = {
    "metadata": metadata,
    "comments": comments,
    "transcript": transcript
}

# Save combined data to a JSON file named after the video ID
output_file = os.path.join('data', f"{video_id}.json")
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(video_data, f, ensure_ascii=False, indent=4)

print(f"Data has been saved to {output_file}.")