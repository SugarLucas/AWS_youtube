import logging
import requests
import boto3
import uuid
import time
from datetime import datetime
from youtube_transcript_api import YouTubeTranscriptApi

def get_video_transcript(video_id):
    """fetch video transcript"""
    try:
        transcript_list = youtube_transcript_api(video_id)
        full_text = ' '.join(entry['text'] for entry in transcript_list)
        print(full_text)
        return full_text
    except Exception as e:
        return "Transcript unavailable"

# API endpoint
API_ENDPOINT = "https://uqahsjj2e6.execute-api.ca-central-1.amazonaws.com/Stage2/get-analysis"

payload = {
    "key1": "value1",
    "key2": "value2"
}

try:
    # Sending the POST request
    response = requests.post(url, headers=headers, json=payload)

    # Raise an HTTPError for bad responses (4xx and 5xx)
    response.raise_for_status()

    # Print response content
    print("Response Status Code:", response.status_code)
    print("Response Body:", response.json())  # Use `.text` for plain text responses

except requests.exceptions.RequestException as e:
    print("Error occurred:", e)


# Initialize DynamoDB
dynamodb = boto3.resource('dynamodb')
DYNAMODB_TABLE = 'g13-436-youtube-data'

class RequestPoller:
    def __init__(self, request_text):
        """
        Initialize the RequestPoller instance.
        """
        self.table = dynamodb.Table(DYNAMODB_TABLE)
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)

        # Generate a unique request ID
        self.req_id = self.generate_req_id(request_text)
        self.request_text = request_text

    def generate_req_id(self, text):
        """
        Generate a unique request ID based on the input text and a UUID.
        """
        hash_input = f"{text}-{uuid.uuid4()}"
        return hashlib.sha256(hash_input.encode()).hexdigest()

    def new_item(self):
        """
        Add a new item to DynamoDB with a status of 'PENDING'.
        """
        self.logger.info(f"Creating new item with ID: {self.req_id}")
        self.table.put_item(
            Item={
                "RequestID": self.req_id,
                "FinalResult": "",
                "RequestStatus": "PENDING"
            }
        )

    def poll(id):
        self.table.
