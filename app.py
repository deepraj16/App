from flask import Flask, render_template, jsonify, request
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled
from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound
import re

app = Flask(__name__)

def extract_video_id(url):
    """Extract video ID from YouTube URL"""
    patterns = [
        r'(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/)([^&\n?#]+)',
        r'youtube\.com\/v\/([^&\n?#]+)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None

def get_video_transcript(video_id):
    """Get transcript from YouTube video"""
    if not video_id:
        raise ValueError("Video ID is not provided.")
    
    try:
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id, languages=["en"])
        transcript = " ".join(chunk["text"] for chunk in transcript_list)
        return transcript
    
    except TranscriptsDisabled:
        return None
    except NoTranscriptFound:
        return None
    except Exception as e:
        print(f"Error: {e}")
        return None

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/transcribe")
def transcribe():
    video_url = request.args.get("videoUrl")
    if not video_url:
        return jsonify({"error": "Video URL is required"}), 400
    
    video_id = extract_video_id(video_url)
    if not video_id:
        return jsonify({"error": "Invalid YouTube URL"}), 400
    
    transcript = get_video_transcript(video_id)
    if transcript is None:
        return jsonify({"error": "Transcript not available for this video"}), 404

    return jsonify({"transcript": transcript, "video_id": video_id}), 200

@app.route("/get_tran", methods=['POST', 'GET'])
def get_tra(): 
    data = request.args.get("video_id")
    if not data:
        return jsonify({"error": "Video ID is required"}), 400
    
    transcript = get_video_transcript(data)
    if transcript is None:
        return jsonify({"error": "Transcript not available for this video"}), 404

    return jsonify({"transcript": transcript}), 200

if __name__ == "__main__":
    app.run(debug=True)