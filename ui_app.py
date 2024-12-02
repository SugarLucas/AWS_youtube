import streamlit as st
import streamlit_shadcn_ui as ui
import json
import request_poller as rp
import comments
import matplotlib.pyplot as plt

# Title and Description
st.markdown(
    """
    <div style="background-color:#000; padding:20px; border-radius:10px;">
        <h1 style="color:#FF0000; text-align:center;">YouTube Data Processor</h1>
        <p style="color:#FFF; text-align:center; font-size:18px;">Analyze YouTube Video Metadata, Comments, and Trends!</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# Input Field for YouTube Video URL
st.markdown("<h3 style='color: #FFF;'>Enter YouTube Video URL:</h3>", unsafe_allow_html=True)
video_url = ui.input(placeholder="https://www.youtube.com/watch?v=3IdJGL_gFYw", key="video_url_input")

# Button for Submission
if ui.button(text="Analyze Video", key="analyze_video_btn"):
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

                    # Video Metadata
                    ui.card(
                        content=st.markdown(
                            f"""
                            <div style="background-color:#1E1E1E; color:#FFF; padding:10px; border-radius:10px;">
                                <h3>Video Metadata</h3>
                                <ul>
                                    <li><strong>Title:</strong> {metadata.get("title", "N/A")}</li>
                                    <li><strong>Channel:</strong> {metadata.get("channel_title", "N/A")}</li>
                                    <li><strong>Views:</strong> {metadata.get("view_count", "N/A")}</li>
                                    <li><strong>Likes:</strong> {metadata.get("like_count", "N/A")}</li>
                                    <li><strong>Comments:</strong> {metadata.get("comment_count", "N/A")}</li>
                                </ul>
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )
                    )

                    # Sentiment Analysis
                    ui.card(
                        content=st.markdown(
                            f"""
                            <div style="background-color:#1E1E1E; color:#FFF; padding:10px; border-radius:10px;">
                                <h3>Sentiment Analysis</h3>
                                <p><strong>Sentiment Score:</strong> {result.get('sentiment_score_percentage', 'N/A')}%</p>
                                <p style="color:#FF0000;">{result.get("sentiment_feedback", "No feedback available")}</p>
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )
                    )

                    # Video Suggestions
                    ui.card(
                        content=st.markdown(
                            """
                            <h3>Video Suggestions</h3>
                            """,
                            unsafe_allow_html=True,
                        )
                    )
                    for idx, suggestion in enumerate(result.get("video_suggestions", "").split("\n")):
                        ui.link_button(text=f"Watch Suggestion {idx+1}", url=suggestion, key=f"video_suggestion_{idx}")

                    # Top Comments and Trends
                    top_liked, top_replied = comments.get_top_comments(data, count=10)
                    trends = comments.get_comment_trends_monthly(data)

                    # Most Liked Comments
                    ui.card(
                        content=st.markdown(
                            """
                            <h3>Most Liked Comments</h3>
                            """,
                            unsafe_allow_html=True,
                        )
                    )
                    for idx, comment in enumerate(top_liked):
                        ui.card(
                            content=st.markdown(
                                f"""
                                <p><strong>{idx+1}. {comment.get('author', 'Anonymous')}:</strong> {comment.get('text', 'No text')} (Likes: {comment.get('likes', 0)})</p>
                                """,
                                unsafe_allow_html=True,
                            )
                        )

                    # Most Replied Comments
                    ui.card(
                        content=st.markdown(
                            """
                            <h3>Most Replied Comments</h3>
                            """,
                            unsafe_allow_html=True,
                        )
                    )
                    for idx, comment in enumerate(top_replied):
                        ui.card(
                            content=st.markdown(
                                f"""
                                <p><strong>{idx+1}. {comment.get('author', 'Anonymous')}:</strong> {comment.get('text', 'No text')} (Replies: {comment.get('reply_count', 0)})</p>
                                """,
                                unsafe_allow_html=True,
                            )
                        )

                    # Monthly Trends
                    ui.card(
                        content=st.markdown(
                            """
                            <h3>Monthly Comment Trends</h3>
                            """,
                            unsafe_allow_html=True,
                        )
                    )
                    if trends:
                        dates, counts = zip(*sorted(trends.items()))
                        plt.figure(figsize=(10, 5))
                        plt.bar(dates, counts, color="#FF0000")
                        plt.title("Monthly Comments", fontsize=16)
                        plt.xlabel("Month", fontsize=14)
                        plt.ylabel("Number of Comments", fontsize=14)
                        plt.xticks(rotation=45)
                        st.pyplot(plt)
                    else:
                        st.info("No comment trends available.")
                else:
                    ui.alert_dialog(
                        title="No Data Returned",
                        description="No data was returned. Please try again.",
                        confirm_label="OK",
                        key="no_data_dialog"
                    )
            except Exception as e:
                ui.alert_dialog(
                    title="Unexpected Error",
                    description=f"An unexpected error occurred: {e}",
                    confirm_label="OK",
                    key="error_dialog"
                )
    else:
        ui.alert_dialog(
            title="Invalid URL",
            description="Please enter a valid YouTube URL!",
            confirm_label="OK",
            key="invalid_url_dialog"
        )
