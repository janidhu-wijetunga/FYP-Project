from youtube_transcript_api import YouTubeTranscriptApi

transcript_file_path = "FYP-Project/transcript.txt"

video_link = "https://www.youtube.com/watch?v=EG8cvSJFCc0"
video_id = video_link.split("v=")[1]

transcript = YouTubeTranscriptApi.get_transcript(video_id)
try:
    with open(transcript_file_path, "w") as f:
        for caption in transcript:
            text = caption['text']
            start_time = caption['start']
            f.write(f"{start_time}: {text}\n")
    print(f"Captions saved")
    
except Exception as e:
    print("An error occurred:", e)