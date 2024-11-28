import logging
import json
import requests
import boto3
import uuid
import time
from datetime import datetime

# Initialize DynamoDB
dynamodb = boto3.resource('dynamodb')
DYNAMODB_TABLE = 'g13-436-youtube-data'
# response = table.get_item(Key = { 'RequestID': "12345" })
# print(response["Item"]["RequestStatus"])

def poll(id, interval=2, timeout=60):
    table = dynamodb.Table(DYNAMODB_TABLE)
    start_time = time.time()

    while time.time() - start_time < timeout:
        response = table.get_item(
            Key={ 
                'RequestID': id
            }
        )

        # Check if the response contains 'Item'
        if "Item" in response and "RequestStatus" in response["Item"]:
            status = response["Item"]["RequestStatus"]

            if status == "Completed":
                if "FinalResult" in response["Item"]:
                    print(f'Success: {status}')
                    return response["Item"]["FinalResult"]
                else:
                    print(f"Completed but missing FinalResult in the response.")
                    return None  # or handle this case differently as needed

        # Wait before polling again
        time.sleep(interval)

    print("Timeout exceeded.")
    return None  # Return None if the timeout is reached without completion

print(poll("12345"))
