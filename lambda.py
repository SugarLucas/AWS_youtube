import json
from googleapiclient.discovery import build
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import TranscriptsDisabled
import boto3
import os
import re

# YouTube API Key and Bucket Name (Set as environment variables for security)
api_key = os.getenv('YOUTUBE_API_KEY', 'YOUR_API_KEY')
bucket_name = os.getenv('S3_BUCKET_NAME', 'YOUR_BUCKET_NAME')

# Initialize YouTube API client
youtube = build('youtube', 'v3', developerKey=api_key)

# Initialize S3 client
s3_client = boto3.client('s3')

def extract_video_id(url):
    """
    Extract the video ID from a YouTube URL.
    """
    match = re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11})", url)
    if match:
        return match.group(1)
    else:
        raise ValueError("Invalid YouTube URL provided.")

def check_existing_analysis(video_id):
    """
    Check if the analysis already exists in S3.
    """
    try:
        s3_client.head_object(Bucket=bucket_name, Key=f"{video_id}.json")
        return True  # File exists
    except Exception as e:
        return False  # File does not exist

def get_video_metadata(video_id):
    """
    Retrieve video metadata based on video ID.
    """
    try:
        response = youtube.videos().list(
            part="snippet,statistics",
            id=video_id
        ).execute()
        
        if not response['items']:
            return {"error": "Video not found"}
        
        metadata = response['items'][0]
        snippet = metadata['snippet']
        statistics = metadata['statistics']
        
        return {
            "video_id": video_id,
            "title": snippet['title'],
            "description": snippet['description'],
            "published_at": snippet['publishedAt'],
            "view_count": statistics.get('viewCount', 0),
            "like_count": statistics.get('likeCount', 0),
            "comment_count": statistics.get('commentCount', 0)
        }
    except Exception as e:
        return {"error": str(e)}

def get_comments(video_id):
    """
    Retrieve comments for a given video ID.
    """
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
        request = youtube.commentThreads().list_next(request, response)
    return comments_data

def get_transcript(video_id):
    """
    Retrieve the transcript for a given video ID.
    """
    try:
        transcript_data = YouTubeTranscriptApi.get_transcript(video_id)
        transcript = [
            {
                'text': entry['text'],
                'start_time': entry['start'],
                'duration': entry['duration']
            } for entry in transcript_data
        ]
        return transcript
    except TranscriptsDisabled:
        return {"error": "Transcript is disabled for this video."}
    except Exception as e:
        return {"error": str(e)}

def save_to_s3(video_id, data):
    """
    Save the analysis data to S3 as a JSON file.
    """
    try:
        s3_client.put_object(
            Bucket=bucket_name,
            Key=f"{video_id}.json",
            Body=json.dumps(data, ensure_ascii=False),
            ContentType='application/json'
        )
        return {"message": f"Data saved to S3 with key {video_id}.json"}
    except Exception as e:
        return {"error": str(e)}

def lambda_handler(event, context):
    """
    Main Lambda handler.
    """
    url = event.get('url', '')
    if not url:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "Missing video URL"})
        }

    try:
        # Extract video ID from URL
        video_id = extract_video_id(url)

        # Check for existing analysis
        if check_existing_analysis(video_id):
            return {
                "statusCode": 200,
                "body": json.dumps({"message": "Analysis already exists in S3"})
            }

        # Retrieve metadata, comments, and transcript
        metadata = get_video_metadata(video_id)
        if "error" in metadata:
            return {
                "statusCode": 404,
                "body": json.dumps(metadata)
            }

        comments = get_comments(video_id)
        transcript = get_transcript(video_id)

        # Prepare analysis data
        analysis_data = {
            "metadata": metadata,
            "comments": comments,
            "transcript": transcript
        }

        # Save to S3
        save_result = save_to_s3(video_id, analysis_data)
        if "error" in save_result:
            return {
                "statusCode": 500,
                "body": json.dumps(save_result)
            }

        # Return success response
        return {
            "statusCode": 200,
            "body": json.dumps(analysis_data, ensure_ascii=False)
        }

    except ValueError as e:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": str(e)})
        }
    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }