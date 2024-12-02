import streamlit as st
import json
import request_poller as rp
import comments
import matplotlib.pyplot as plt

# Title and Description
st.title("YouTube Data Processor")
st.markdown("<p style='text-align: center; font-size: 18px;'>Enter a YouTube video URL to analyze its metadata, comments, and trends!</p>", unsafe_allow_html=True)

# Input Field for YouTube Video URL
video_url = st.text_input("Enter YouTube Video URL", placeholder="https://www.youtube.com/watch?v=3IdJGL_gFYw")

if st.button("Submit"):
    if video_url:
        with st.spinner("Processing..."):
            try:
                # Extract Video ID
                video_id = comments.extract_video_id(video_url)

                # Fetch Metadata
                metadata = comments.get_video_metadata(video_id)

                # Get Comments
                data = comments.get_comments(video_url)  # Retrieve all comments
                comment_data = comments.extract_content(data)  # Extract content for poller

                # Run Poller
                poller = rp.RequestPoller(video_url, comment_data)
                request_id = poller.req_id
                final = poller.poll()

                if final:
                    result = json.loads(final)  # Assuming the result is JSON

                    # Display Metadata
                    st.subheader("Video Metadata")
                    st.markdown(
                        f"""
                        <div style='font-size:16px; text-align:justify;'>
                            <strong>Title:</strong> {metadata.get("title", "N/A")}<br>
                            <strong>Channel:</strong> {metadata.get("channel_title", "N/A")}<br>
                            <strong>Views:</strong> {metadata.get("view_count", "N/A")}<br>
                            <strong>Likes:</strong> {metadata.get("like_count", "N/A")}<br>
                            <strong>Comments:</strong> {metadata.get("comment_count", "N/A")}<br>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                    # Display Sentiment Results
                    st.subheader("Sentiment Analysis")
                    st.markdown(
                        f"""
                        <div style='font-size:24px; font-weight:bold; text-align:center; color:#FF4B4B;'>
                            Sentiment Score: {result.get('sentiment_score_percentage', 'N/A')}
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                    st.info(result.get("sentiment_feedback", "No feedback available"))

                    # Display Video Suggestions
                    st.subheader("Video Suggestions")
                    suggestions = result.get("video_suggestions", "").split("\n")
                    for suggestion in suggestions:
                        st.button(
                            suggestion,  # Display the entire link
                            key=suggestion,
                            on_click=lambda s=suggestion: st.write(f"[Open Link]({s})"),
                        )

                   # Display Top Comments and Trends
                    st.subheader("Top Comments and Trends")
                    top_liked, top_replied = comments.get_top_comments(data, count=10)
                    trends = comments.get_comment_trends_monthly(data)

                    # Top Liked Comments
                    st.markdown("### **Most Liked Comments:**")
                    for idx, comment in enumerate(top_liked, start=1):
                        st.markdown(
                            f"**{idx}. {comment.get('author', 'Anonymous')}:** {comment.get('text', 'No text')} "
                            f"(Likes: {comment.get('likes', 0)})"
                        )

                    # Top Replied Comments
                    st.markdown("### **Most Replied Comments:**")
                    for idx, comment in enumerate(top_replied, start=1):
                        st.markdown(
                            f"**{idx}. {comment.get('author', 'Anonymous')}:** {comment.get('text', 'No text')} "
                            f"(Replies: {comment.get('reply_count', 0)})"
                        )

                    # Comment Trends
                    st.markdown("### **Monthly Comment Trends**")
                    if trends:
                        dates, counts = zip(*sorted(trends.items()))
                        plt.figure(figsize=(10, 5))
                        plt.plot(dates, counts, marker="o", color="#FF4B4B", linestyle="--")
                        plt.title("Number of Comments Over Months", fontsize=16)
                        plt.xlabel("Month", fontsize=14)
                        plt.ylabel("Number of Comments", fontsize=14)
                        plt.xticks(rotation=45)
                        st.pyplot(plt)
                    else:
                        st.info("No comment trends available.")
                else:
                    st.error("No data was returned. Please try again.")
            except json.JSONDecodeError:
                st.error("Error processing the results. Please try again.")
            except Exception as e:
                st.error(f"An unexpected error occurred: {e}")
    else:
        st.error("Please enter a valid YouTube URL!")
