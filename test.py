import os
import json
import boto3
import streamlit as st
from urllib.parse import urlparse, parse_qs
import subprocess

# AWS S3 Configuration
S3_BUCKET = '436-transcriptions'

# Initialize S3 clients3_client = boto3.client('s3')


# Helper Functions
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

def run_youtube_script(video_id):
    """Run the youtube.py script with the given video ID."""
    try:
        result = subprocess.run(
            ["python3", "youtube.py", video_id],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            return True
        else:
            st.error(f"Error running script: {result.stderr}")
            return False
    except Exception as e:
        st.error(f"Error running script: {e}")
        return False

# AWS Lambda Configuration
LAMBDA_FUNCTION_NAME = 'save_s3'  # Replace with your Lambda function name

# Initialize Lambda client
lambda_client = boto3.client('lambda', region_name='ca-central-1')

def upload_to_s3(file_path):
    """Upload a file to S3 using a Lambda function."""
    try:
        # Read file content
        with open(file_path, 'r', encoding='utf-8') as f:
            file_content = f.read()

        # Prepare the payload for Lambda
        payload = {
            'file_name': os.path.basename(file_path),
            'file_content': file_content
        }

        # Invoke Lambda function
        response = lambda_client.invoke(
            FunctionName=LAMBDA_FUNCTION_NAME,
            InvocationType='RequestResponse',
            Payload=json.dumps(payload)
        )

        # Parse the Lambda response
        response_payload = json.loads(response['Payload'].read())
        if response_payload['statusCode'] == 200:
            print(response_payload['body'])
        else:
            print(f"Lambda error: {response_payload['body']}")
    except Exception as e:
        print(f"Error invoking Lambda: {e}")

# Page Configuration
st.set_page_config(
    page_title="YouTube Video Analysis",
    page_icon="📊 ",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Title and description
st.title("YouTube Video Analysis 🎥 ")
st.subheader("Analyze YouTube video metadata, comments, and transcript! 🤖 ")
st.markdown("Enter a YouTube video URL to analyze its content.")

# Input Section
video_url = st.text_input("Enter YouTube Video URL", placeholder="https://youtu.be/abc123")

if st.button("Analyze Video"):
    if video_url:
        video_id = extract_video_id(video_url)
        if video_id:
            with st.spinner("Analyzing... Please wait."):
                if run_youtube_script(video_id):
                    # Combine JSON file path
                    file_path = os.path.join('data', f"{video_id}.json")

                    # Upload the generated JSON file to S3
                    if os.path.exists(file_path):
                        upload_to_s3(file_path)

                    # Load and display data
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            video_data = json.load(f)

                        # Display Metadata
                        st.header("Video Metadata")
                        metadata = video_data["metadata"]
                        st.markdown(f"**Title**: {metadata.get('title', 'N/A')}")
                        st.markdown(f"**Description**: {metadata.get('description', 'N/A')}")
                        st.markdown(f"**Channel**: {metadata.get('channel_title', 'N/A')}")
                        st.markdown(f"**Publish Date**: {metadata.get('publish_date', 'N/A')}")
                        st.markdown(f"**Views**: {metadata.get('view_count', '0')}")
                        st.markdown(f"**Likes**: {metadata.get('like_count', '0')}")
                        st.markdown(f"**Comments**: {metadata.get('comment_count', '0')}")
                        st.markdown(f"**Duration**: {metadata.get('duration', 'N/A')}")

                        # Display Comments
                        st.header("Comments")
                        comments = video_data["comments"]
                        if comments:
                            for comment in comments:
                                st.markdown(f"- **{comment['author']}**: {comment['text']} "
                                            f"({comment['likes']} likes)")
                        else:
                            st.markdown("No comments found.")

                        # Display Transcript
                        st.header("Transcript")
                        transcript = video_data["transcript"]
                        if isinstance(transcript, list):
                            for entry in transcript:
                                st.markdown(f"- **{entry['start_time']}s**: {entry['text']}")
                        else:
                            st.markdown(transcript.get("error", "No transcript available."))
                    except FileNotFoundError as e:
                        st.error(f"File not found: {e}")
                    except json.JSONDecodeError as e:
                        st.error(f"Error decoding JSON: {e}")
                else:
                    st.error("Failed to analyze the video.")
        else:
            st.error("Invalid YouTube URL. Please enter a valid URL.")
    else:
        st.error("Please enter a YouTube URL.")

# Footer
st.markdown("---")
st.markdown("Developed by **LAAMA Team**.")
                                                                   
                                                                  