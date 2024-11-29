from youtube_transcript_api import YouTubeTranscriptApi
import json
import os

def get_transcript(video_id):
    """Fetch YouTube transcript for a given video ID."""
    try:
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
        # Concatenate all text entries into a single string
        full_text = " ".join([entry["text"] for entry in transcript_list])
        return {"video_id": video_id, "transcript": full_text}
    except Exception as e:
        return {"error": str(e)}

def save_transcript_to_file(video_id, transcript, output_dir="data"):
    """Save the transcript to a JSON file."""
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    file_path = os.path.join(output_dir, f"{video_id}.json")
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(transcript, f, ensure_ascii=False, indent=4)
    return file_path