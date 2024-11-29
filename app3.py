import streamlit as st
import json
import boto3
import request_poller as rp
import comments

st.title("YouTube Data Processor")
st.markdown("Enter a YouTube video URL to process its transcript and save data to S3.")

video_url = st.text_input("Enter YouTube Video URL", placeholder="https://www.youtube.com/watch?v=3IdJGL_gFYw")

if st.button("Submit"):
    data = comments.get_comments(video_url)
    comment_data = comments.extract_content(data)
    poller = rp.RequestPoller(video_url, comment_data)
    request_id = poller.req_id
    final = poller.poll()
    if video_url:
        with st.spinner("Processing..."):
            st.markdown(final)
