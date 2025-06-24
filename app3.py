from flask import Flask, render_template, jsonify, request
import requests
import re
import os

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

def get_transcript_rapidapi(video_id):
    """Get transcript using RapidAPI YouTube Transcript API"""
    
    # Your RapidAPI key
    api_key = "aa1b4a6932mshbeb683ba4c15e85p1340a8jsn22a230a7d684"
    
    # Correct API endpoint based on your curl command
    url = "https://youtube-transcript3.p.rapidapi.com/api/transcript"
    
    # Parameters - using videoId as shown in your curl command
    querystring = {"videoId": video_id}
    
    headers = {
        "x-rapidapi-key": api_key,
        "x-rapidapi-host": "youtube-transcript3.p.rapidapi.com"
    }
    
    try:
        print(f"Making request to RapidAPI for video ID: {video_id}")
        response = requests.get(url, headers=headers, params=querystring, timeout=30)
        
        print(f"Response status: {response.status_code}")
        print(f"Response content: {response.text[:500]}...")  # First 500 chars for debugging
        
        if response.status_code == 200:
            data = response.json()
            
            # Handle different response formats
            if isinstance(data, list) and len(data) > 0:
                # If response is a list of transcript segments
                transcript_text = ' '.join([item.get('text', '') for item in data if 'text' in item])
                return transcript_text
            elif isinstance(data, dict):
                # If response is a dictionary, check for common transcript fields
                if 'transcript' in data:
                    if isinstance(data['transcript'], list):
                        transcript_text = ' '.join([item.get('text', '') for item in data['transcript'] if 'text' in item])
                        return transcript_text
                    else:
                        return str(data['transcript'])
                elif 'text' in data:
                    return data['text']
                elif 'data' in data and isinstance(data['data'], list):
                    transcript_text = ' '.join([item.get('text', '') for item in data['data'] if 'text' in item])
                    return transcript_text
                elif 'results' in data:
                    return str(data['results'])
                else:
                    # Return the whole response if we can't parse it
                    return str(data)
            
            # If we can't parse the response, return it as string
            return str(data)
        
        elif response.status_code == 429:
            return "Rate limit exceeded. Please try again later."
        elif response.status_code == 404:
            return "Transcript not found for this video."
        elif response.status_code == 403:
            return "API access forbidden. Check your API key."
        else:
            return f"API Error: {response.status_code} - {response.text}"
            
    except requests.exceptions.Timeout:
        return "Request timed out. Please try again."
    except requests.exceptions.RequestException as e:
        print(f"Request error: {e}")
        return f"Network error: {str(e)}"
    except Exception as e:
        print(f"Unexpected error: {e}")
        return f"Unexpected error: {str(e)}"

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/transcribe")
def transcribe():
    video_url = request.args.get("videoUrl")
    
    if not video_url:
        return jsonify({"error": "Video URL is required"}), 400
    
    # Extract video ID from URL
    video_id = extract_video_id(video_url)
    if not video_id:
        return jsonify({"error": "Invalid YouTube URL"}), 400
    
    print(f"Extracted video ID: {video_id}")
    
    # Get transcript using RapidAPI
    transcript = get_transcript_rapidapi(video_id)
    
    if not transcript:
        return jsonify({"error": "Transcript not available for this video"}), 404
    
    # Check if transcript is an error message
    if any(error_msg in transcript for error_msg in ["Rate limit", "API Error", "Network error", "not found", "forbidden"]):
        return jsonify({"error": transcript}), 500

    return jsonify({
        "transcript": transcript, 
        "video_id": video_id,
        "source": "RapidAPI YouTube Transcript"
    }), 200

@app.route("/test")
def test_api():
    """Test endpoint to check if API is working"""
    # Test with the video ID from your curl command
    test_video_id = "ZacjOVVgoLY"
    transcript = get_transcript_rapidapi(test_video_id)
    
    return jsonify({
        "test_video_id": test_video_id,
        "api_working": bool(transcript and not any(error in transcript for error in ["Error", "error", "forbidden", "not found"])),
        "transcript_preview": transcript[:200] + "..." if transcript and len(transcript) > 200 else transcript
    })

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)  # Set debug=True for local testing