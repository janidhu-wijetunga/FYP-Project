from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import TranscriptsDisabled
from pytube import YouTube
from googleapiclient.discovery import build
from dotenv import load_dotenv
import os
from flask import Flask, render_template, request

# API key for youtube API v3.
load_dotenv()
api_key = os.getenv("API_KEY")

comments_file_path = "comments.txt"
transcript_file_path = "transcript.txt"

# Define flask back end.
app = Flask(__name__)
@app.route('/', methods=['GET', 'POST'])
def index():

    video_link = ""
    video_id = ""
    transcript_file_content = ""
    comments_file_content = ""

    if request.method == 'POST':

        video_link = request.form.get('input_link')

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
        
        # Read transcripts from the file and assign to a variable.
        if os.path.exists(transcript_file_path):
            with open(transcript_file_path, "r") as file:
                transcript_file_content = file.read()
        else:
            print("No existing file.")

        # Read comments from the file and assign to a variable.
        if os.path.exists(transcript_file_path):
            with open(comments_file_path, "r", encoding='utf-8') as file:
                comments_file_content = file.read()
        else:
            print("No existing file.")
        
    return render_template('index.html', py_variable_captions=transcript_file_content, py_variable_comments=comments_file_content, link = video_link)
    
# To clear existing data.
@app.route('/delete', methods=['POST'])
def delete_file():
    output = ""
    if os.path.exists(transcript_file_path):
        os.remove(transcript_file_path)
        os.remove(comments_file_path)
        output = "Data cleared successfully."
    else:
        output = "Data not found."
    
    clear_value = ""
    return render_template('index.html', delete_message = output, py_variable_captions = clear_value, py_variable_comments = clear_value, link = clear_value)

if __name__ == '__main__':
    app.run(debug=True)