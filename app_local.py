import streamlit as st
from youtube import get_transcript, save_transcript_to_file
import os

# Directory to save transcripts
DATA_FOLDER = "data"

def extract_video_id(url):
    """Extract the video ID from a YouTube URL."""
    if "v=" in url:
        return url.split("v=")[1].split("&")[0]
    elif "youtu.be/" in url:
        return url.split("youtu.be/")[1].split("?")[0]
    else:
        return None

# Ensure the data folder exists
if not os.path.exists(DATA_FOLDER):
    os.makedirs(DATA_FOLDER)

# Streamlit UI
st.title("Local YouTube Transcript Saver")
st.markdown("Enter a YouTube video URL to fetch its transcript and save it locally in the 'data' folder.")

# User input
video_url = st.text_input("Enter YouTube Video URL", placeholder="https://youtu.be/example")

if st.button("Submit"):
    if video_url:
        with st.spinner("Fetching transcript..."):
            # Step 1: Extract video ID
            video_id = extract_video_id(video_url)
            if not video_id:
                st.error("Invalid YouTube URL. Please enter a valid URL.")
            else:
                # Step 2: Fetch the transcript using youtube.py
                transcript_data = get_transcript(video_id)

                # Step 3: Handle errors or save the transcript
                if "error" in transcript_data:
                    st.error(f"Error fetching transcript: {transcript_data['error']}")
                else:
                    # Save transcript to the data folder
                    file_path = save_transcript_to_file(video_id, transcript_data, output_dir=DATA_FOLDER)
                    st.success(f"Transcript saved successfully to {file_path}")

                    # Display the transcript in the UI
                    st.text_area("Transcript", transcript_data["transcript"], height=300)
    else:
        st.error("Please enter a valid YouTube URL.")