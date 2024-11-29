import sys
import streamlit as st
import os
import json
from googleapiclient.discovery import build
# from youtube_transcript_api import YouTubeTranscriptApi
# from youtube_transcript_api._errors import TranscriptsDisabled
import boto3
from urllib.parse import urlparse, parse_qs
import subprocess

api_key = 'AIzaSyBLZYlWDGGfjWSef1eGz5bMsPJzj9jrwJY'
# video_id = sys.argv[1]
os.makedirs('data', exist_ok=True)
youtube = build('youtube', 'v3', developerKey=api_key)

def extract_video_id(url):
    """Extract the video ID from a YouTube URL."""
    try:
        parsed_url = urlparse(url)
        if parsed_url.hostname in ['www.youtube.com', 'youtube.com']:
            return parse_qs(parsed_url.query).get('v', [None])[0]
        elif parsed_url.hostname == 'youtu.be':
            return parsed_url.path.lstrip('/')
    except Exception as e:
        st.error(f"Error extracting video ID: {e}")
        return None
    return None

def get_comments(url):
    """Retrieve comments for the given video ID."""
    video_id = extract_video_id(url)
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

def extract_content(comments_data): 
    all_text = " ".join(entry['text'] for entry in comments_data)
    return all_text

