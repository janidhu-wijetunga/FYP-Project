from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import TranscriptsDisabled
from pytube import YouTube
from googleapiclient.discovery import build

# API key for youtube API v3.
api_key = "AIzaSyAa-L-MgfgRKi9OfOzhF2Xs4NdMCKoBGak"

video_link = "https://www.youtube.com/watch?v=LtFeTNduo18"

comments_file_path = "comments.txt"
transcript_file_path = "transcript.txt"

# Split the video link to get the video id.
video_id = video_link.split("v=")[1]

# Extract the video captions.
try:
    transcript = YouTubeTranscriptApi.get_transcript(video_id)

    with open(transcript_file_path, "w") as f:
        for caption in transcript:
            text = caption['text']
            start_time = caption['start']
            f.write(f"{start_time}: {text}\n")
    print(f"Captions saved.")

# Error handling if captions are disabled.
except TranscriptsDisabled:
    print("Transcripts are disabled for this video.")
    with open(transcript_file_path, "w") as f:
        f.write("Transcripts are disabled for this video.")


# Create a YouTube Data API client.
youtube = build('youtube', 'v3', developerKey=api_key)

# Fetch video comments.
response = youtube.commentThreads().list(
    part='snippet',
    videoId=video_id,
    textFormat='plainText'
).execute()

# Save comments.
if response['items']:
    with open(comments_file_path, 'w', encoding='utf-8') as f:
        for comment in response['items']:
            comment_text = comment['snippet']['topLevelComment']['snippet']['textDisplay']
            commenter_name = comment['snippet']['topLevelComment']['snippet']['authorDisplayName']
            f.write(f"{commenter_name}: {comment_text} \n\n")
    print("Comments saved.")
else:
    print("No comments for this video")
    with open(comments_file_path, "w") as f:
        f.write("No comments for this video.")