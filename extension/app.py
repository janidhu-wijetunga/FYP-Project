from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import TranscriptsDisabled
from pytube import YouTube
import requests
from googleapiclient.discovery import build
from dotenv import load_dotenv
import os
from flask import Flask, render_template, request, jsonify
import pytesseract
from PIL import Image
from flask_cors import CORS

# API key for youtube API v3.
load_dotenv()
api_key = os.getenv("API_KEY")

comments_file_path = "FYP-Project/extension/comments.txt"
transcript_file_path = "FYP-Project/extension/transcript.txt"
thumbnail_file_path = "FYP-Project/extension/thumbnail.jpg"
thumbnail_text_file_path = "FYP-Project/extension/thumbnailText.txt"
description_file_path = "FYP-Project/extension/description.txt"
title_file_path = "FYP-Project/extension/title.txt"

# Define flask back end.
app = Flask(__name__)
CORS(app)
@app.route('/receive_url', methods=['POST'])
def index():

    video_link = ""
    video_id = ""
    transcript_file_content = ""
    comments_file_content = ""
    video_title = ""
    video_description = ""
    thumbnail_text = ""

    if request.method == 'POST':

        data = request.get_json()
        video_link = data.get('url')

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


        # Extract YouTube thumbnail image.
        try:
            yt = YouTube(video_link)
            thumbnail_url = yt.thumbnail_url

            response = requests.get(thumbnail_url)
            if response.status_code == 200:
                with open(thumbnail_file_path, 'wb') as file:
                    file.write(response.content)
                print("Thumbnail saved.")
            else:
                print("Failed to download thumbnail.")
        except Exception as e:
            print("Error:", e)


        # Extract YouTube video description.
        try:
            youtube = build('youtube', 'v3', developerKey=api_key)
            response = youtube.videos().list(
                part="snippet",
                id=video_id
            ).execute()

            if "items" in response and len(response["items"]) > 0:
                video_description = response["items"][0]["snippet"]["description"]
                with open(description_file_path, 'w', encoding='utf-8') as file:
                    file.write(video_description)
                print("Description Saved.")
            else:
                print("Video description not available.")
                with open(description_file_path, 'w', encoding='utf-8') as file:
                    file.write("Video description not available.")

        except Exception as e:
            print("Error:", e)


        # Extract YouTube video title.
        try:
            youtube = build("youtube", "v3", developerKey=api_key)
        
            response = youtube.videos().list(
                part="snippet",
                id=video_id
            ).execute()

            if "items" in response and len(response["items"]) > 0:
                video_title = response["items"][0]["snippet"]["title"]
                print("Video title saved.")
                with open(title_file_path, 'w', encoding='utf-8') as file:
                    file.write(video_title)
            else:
                print("Video title not available.")
                with open(description_file_path, 'w', encoding='utf-8') as file:
                    file.write("Video title not available.")
            
        except Exception as e:
            print("Error:", e)


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
        

        # Extract text from YouTube video thumbnail.
        try:
            image = Image.open(thumbnail_file_path)
            resized_image = image.resize((800, 600))
            thumbnail_text = pytesseract.image_to_string(resized_image, lang='eng', config='--psm 6')
            with open(thumbnail_text_file_path, "w") as f:
                f.write(thumbnail_text)
                print("Thumbnail text saved.")
        
        except Exception as e:
            print("Error:", e)

    return jsonify({"value": video_title})
    
# To clear existing data.
@app.route('/delete', methods=['POST'])
def delete_file():
    output = ""
    if os.path.exists(transcript_file_path):
        os.remove(transcript_file_path)
        os.remove(comments_file_path)
        os.remove(thumbnail_file_path)
        os.remove(thumbnail_text_file_path)
        os.remove(description_file_path)
        os.remove(title_file_path)
        output = "Data cleared successfully."
    else:
        output = "Data not found."
    
    clear_value = ""
    return render_template('index.html', delete_message = output, py_variable_captions = clear_value, py_variable_comments = clear_value, link = clear_value, py_variable_title = clear_value, py_variable_description = clear_value, py_variable_thumbnail = clear_value)

if __name__ == '__main__':
    app.run(debug=True, port=8080)