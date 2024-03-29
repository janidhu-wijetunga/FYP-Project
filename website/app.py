from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import TranscriptsDisabled
from pytube import YouTube
import requests
from googleapiclient.discovery import build
from dotenv import load_dotenv
import os
from flask import Flask, render_template, request
import pytesseract
from PIL import Image
import tensorflow
import numpy as np
import pandas as pd
import re
from transformers import BertTokenizer, BertForSequenceClassification
import torch
from torch.utils.data import DataLoader, TensorDataset

# API key for youtube API v3.
load_dotenv()
api_key = os.getenv("API_KEY")

# Paths to all files required.
comments_file_path = "FYP-Project/website/data/comments.txt"
transcript_file_path = "FYP-Project/website/data/transcript.txt"
thumbnail_file_path = "FYP-Project/website/data/thumbnail.jpg"
thumbnail_text_file_path = "FYP-Project/website/data/thumbnailText.txt"
description_file_path = "FYP-Project/website/data/description.txt"
title_file_path = "FYP-Project/website/data/title.txt"
hate_links_file_path = "FYP-Project/website/data/hateLinks.txt"
bilstm_model_path = "FYP-Project/website/models/bilstm"
bad_words_csv = "FYP-Project/website/models/bad-words.csv"
bad_words_file_path = "FYP-Project/website/data/badWords.txt"
bert_model_path = "FYP-Project/website/models/bert"


# function for the prediction model.
def prediction(text):

    # BILSTM Model.
    trained_model = tensorflow.keras.models.load_model(bilstm_model_path)
    predictions_trained = trained_model.predict(np.array([text]))
    print(*predictions_trained[0])

    if predictions_trained[0] > 0:
        print('BILSTM Prediction: Hate')
        bilstm_prediction_value = "Hate"
    else:
        print('BILSTM Prediction: Not Hate')
        bilstm_prediction_value = "Not Hate"
    

    # Hate words detection.
    detected_bad_words = []
    bad_words_df = pd.read_csv(bad_words_csv, header=None, names=["Bad Word"])
    bad_words_set = set(bad_words_df["Bad Word"])

    with open(bad_words_file_path, "w") as output:
        for line in text.splitlines():
            line = line.strip()  # Remove leading/trailing whitespace
            found_bad_words = []

            for bad_word in bad_words_set:
                pattern = r'\b' + re.escape(bad_word.lower()) + r'\b'
                if re.search(pattern, line.lower()):
                    found_bad_words.append(bad_word)

            if found_bad_words:
                detected_bad_words.append((line, found_bad_words))
                output.write(f"{', '.join(found_bad_words)}\n")

    if os.path.getsize(bad_words_file_path) > 0:
        print("Words Prediction: Detected bad words")
        words_prediction_value = "Hate"
    else:
        print("Words Prediction: No bad words detected")
        words_prediction_value = "Not Hate"


    # BERT Model.
    device = torch.device('cuda') if torch.cuda.is_available() else torch.device('cpu')

    model_name = bert_model_path
    Bert_Tokenizer = BertTokenizer.from_pretrained(model_name)
    Bert_Model = BertForSequenceClassification.from_pretrained(
        model_name).to(device)

    count = 0
    for line in text.splitlines():

        user_input = [line]
 
        user_encodings = Bert_Tokenizer(
            user_input, truncation=True, padding=True, return_tensors="pt")
 
        user_dataset = TensorDataset(
            user_encodings['input_ids'], user_encodings['attention_mask'])
 
        user_loader = DataLoader(user_dataset, batch_size=1, shuffle=False)
 
        Bert_Model.eval()
        with torch.no_grad():
            for batch in user_loader:
                input_ids, attention_mask = [t.to(device) for t in batch]
                outputs = Bert_Model(input_ids, attention_mask=attention_mask)
                logits = outputs.logits
                predictions = torch.sigmoid(logits)
 
        predicted_labels = (predictions.cpu().numpy() > 0.5).astype(int)
        labels_list = ['toxic', 'severe_toxic', 'obscene',
                       'threat', 'insult', 'identity_hate']
        predicted_labels_names = [labels_list[i] for i in range(len(labels_list)) if predicted_labels[0][i] == 1]

        if predicted_labels_names != []:
            count = count + 1

    if count == 0:
        print("BERT Prediction: Not Hate")
        bert_prediction_value = "Not Hate"
    else:
        print("BERT Prediction: Hate")
        bert_prediction_value = "Hate"

    
    # Ensemble Prediction
    ensemble_hate_count = sum(1 for v in [ bilstm_prediction_value, words_prediction_value, bert_prediction_value ] if v == "Hate")
    threshold = 2

    if ensemble_hate_count >= threshold:
        print("Ensemble Prediction: Hate")
        ensemble_prediction = "Hate"
    else:
        print("Ensemble Prediction: Not Hate")
        ensemble_prediction = "No Hate"

    return ensemble_prediction


# Define flask back end.
app = Flask(__name__)
@app.route('/', methods=['GET', 'POST'])
def index():

    # Defining the required variables.
    video_link = ""
    video_id = ""
    transcript_file_content = ""
    comments_file_content = ""
    video_title = ""
    video_description = ""
    thumbnail_text = ""

    transcript_prediction = ""
    comments_prediction = ""
    title_prediction = ""
    description_prediction = ""
    thumbnail_prediction = ""

    if request.method == 'POST':

        video_link = request.form.get('input_link')

        # Split the video link to get the video id.
        video_id_part = video_link.split('&')[0]
        video_id = video_id_part.split("v=")[1]

        # Go through each line of the file to check whether link exists.
        found = False
        with open(hate_links_file_path, "r") as file:
            for line in file:
                if video_id_part in line:
                    found = True
                    break
        
        if found:
            print("Link Exists")

            transcript_prediction = "Hate"
            comments_prediction = "Hate"
            title_prediction = "Hate"
            description_prediction = "Hate"
            thumbnail_prediction = "Hate"

        else:
            print("Link Doesn't Exist")


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

                    title_prediction = prediction(video_title)
                    print("Hate Speech in Title:", title_prediction)
                else:
                    print("Video title not available.")
                    with open(description_file_path, 'w', encoding='utf-8') as file:
                        file.write("Video title not available.")
            
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

                    description_prediction = prediction(video_description)
                    print("Hate Speech in Description:", description_prediction)
                else:
                    print("Video description not available.")
                    with open(description_file_path, 'w', encoding='utf-8') as file:
                        file.write("Video description not available.")

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

                    transcript_prediction = prediction(transcript_file_content)
                    print("Hate Speech in Transcript:", transcript_prediction)
            else:
                print("No existing file.")


            # Read comments from the file and assign to a variable.
            if os.path.exists(transcript_file_path):
                with open(comments_file_path, "r", encoding='utf-8') as file:
                    comments_file_content = file.read()

                    comments_prediction = prediction(comments_file_content)
                    print("Hate Speech in Comments:", comments_prediction)
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
                    
                    thumbnail_prediction = prediction(thumbnail_text)
                    print("Hate Speech in Thumbnail:", thumbnail_prediction)
        
            except Exception as e:
                print("Error:", e)

            if (transcript_prediction == "Hate" or comments_prediction == "Hate" or title_prediction == "Hate" or description_prediction == "Hate" or thumbnail_prediction == "Hate"):
                with open(hate_links_file_path, "a") as file:
                    file.write("\n" + video_id_part + "\n")

        
    return render_template('index.html', py_variable_captions=transcript_prediction, py_variable_comments=comments_prediction, link = video_link, video_id = video_id, py_variable_title = title_prediction, py_variable_description = description_prediction, py_variable_thumbnail = thumbnail_prediction)
    
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
        os.remove(bad_words_file_path)
        output = "Data cleared successfully."
    else:
        output = "Data not found."
    
    clear_value = ""
    return render_template('index.html', delete_message = output, py_variable_captions = clear_value, py_variable_comments = clear_value, link = clear_value, py_variable_title = clear_value, py_variable_description = clear_value, py_variable_thumbnail = clear_value)

if __name__ == '__main__':
    app.run(debug=True)