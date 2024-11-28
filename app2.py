import streamlit as st
import json
import boto3

# AWS Configuration
LAMBDA_FUNCTION_NAME = 'TrialTranscriber'  # Replace with your Lambda function name
REGION = 'ca-central-1'  # Replace with your Lambda function region

# Initialize Lambda client
lambda_client = boto3.client('lambda', region_name=REGION)

def invoke_lambda(video_url, request_id):
    """Invoke the Lambda function to process YouTube data."""
    try:
        # Prepare the payload
        payload = {
            "video_url": video_url,
            "request_id": request_id
        }

        # Call the Lambda function
        response = lambda_client.invoke(
            FunctionName=LAMBDA_FUNCTION_NAME,
            InvocationType='RequestResponse',
            Payload=json.dumps({"body": payload})
        )

        # Parse and return the response
        response_payload = json.loads(response['Payload'].read())
        return response_payload
    except Exception as e:
        st.error(f"Error invoking Lambda: {str(e)}")
        return None
    
# Streamlit UI
st.title("YouTube Data Processor")
st.markdown("Enter a YouTube video URL to process its transcript and save data to S3.")

# User input
video_url = st.text_input("Enter YouTube Video URL", placeholder="https://youtu.be/example")
request_id = st.text_input("Enter a Request ID", placeholder="Unique Request ID")

if st.button("Submit"):
    if video_url and request_id:
        with st.spinner("Processing..."):
            lambda_response = invoke_lambda(video_url, request_id)

            if lambda_response:
                status_code = lambda_response.get("statusCode")
                response_body = json.loads(lambda_response.get("body", "{}"))

                if status_code == 200:
                    st.success("Processing successful!")
                    st.json(response_body)
                else:
                    st.error(f"Error: {response_body.get('error', 'Unknown error')}")
    else:
        st.error("Please enter both a YouTube URL and a Request ID.")
