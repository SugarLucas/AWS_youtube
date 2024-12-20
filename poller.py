import logging
import json
import requests
import boto3
import uuid
import time
from datetime import datetime
from youtube_transcript_api import YouTubeTranscriptApi

API_ENDPOINT = "https://uqahsjj2e6.execute-api.ca-central-1.amazonaws.com/Stage2/get-analysis"

def make_request(video_url, request_id):
    data = {
        "body": {
            "video_url": video_url,
            "request_id": request_id
        }
    }

    headers = {
        "Content-Type": "application/json"
    }

    # requests.post(API_ENDPOINT, headers=headers, data=json.dumps(data))
    try:
        response = requests.post(API_ENDPOINT, headers=headers, json=data)
        response.raise_for_status()  
        return response.json()  
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return None

# Initialize DynamoDB
dynamodb = boto3.resource('dynamodb')
DYNAMODB_TABLE = 'g13-436-youtube-data'

class RequestPoller:
    def __init__(self, url):
        """
        Initialize the RequestPoller instance.
        """
        self.table = dynamodb.Table(DYNAMODB_TABLE)
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)

        # Generate a unique request ID
        self.req_id = self.generate_req_id(url)
        self.url = url 

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

    def poll(self, interval=5, timeout=60):
        make_request(self.req_id, self.url)
        start_time = time.time()
        while time.time() - start_time < timeout:
            response = self.table.get_item(
                Key = { 
                    'RequestID': self.request_id
                }
            )
            
            if "RequestStatus" in response["Item"]:
                status = response["Item"]["RequestStatus"]
                if status == "Completed":   
                    self.logger.info(f"Request {self.request_id} completed successfully!")
                    if "FinalResult" in response:
                        return response["Item"]["FinalResult"]

                else:
                    self.logger.info(f"Request {self.request_id} status: {status}. Retrying in {interval} seconds.")

                else:
                    self.logger.warning(f"Request ID {self.req_id} not found in the table.")

            time.sleep(interval)


