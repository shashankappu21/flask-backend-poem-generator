import google.generativeai as genai
from flask import Flask
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import time

# Configure the API key
genai.configure(api_key='AIzaSyAJBQa_hLSdOSByytzF7R_2R3tAEFmVQQ0')

model = genai.GenerativeModel("gemini-1.5-flash")

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "http://192.168.1.*"}})
socketio = SocketIO(app, cors_allowed_origins="*") 

# Helper function to process emotions
def process_emotions(emotion_str):
    emotions = emotion_str.split(", ")
    emotion_dict = {}
    emotion_labels = ["joy", "sadness", "neutral", "disgust", "fear", "anger", "surprise"]
    
    for i, emotion in enumerate(emotion_labels):
        score = float(emotions[i].split(": ")[1])
        emotion_dict[emotion] = score
    
    return emotion_dict

@socketio.on('send_prompt')
def handle_message(data):
    prompt = data.get('prompt')
    emotion_str = data.get('emotionString')  # Expecting the emotion string in the format "joy: 0.9, sadness: 0.05, neutral: 0.02, disgust: 0.01, fear: 0.01, anger: 0.01, surprise: 0.0"

    # Process emotions string into a dictionary format
    emotion_data = process_emotions(emotion_str)

    # Construct the full prompt
    full_prompt = f"Generate a poem using the following prompt: '{prompt}'. Consider the user's current emotional state: {emotion_str}. The poem should subtly reflect or respond to these emotions."

    stream = model.generate_content(full_prompt, stream=True)
    poem = ""
    for response in stream:
        poem_chunk = response.text
        poem += poem_chunk
        time.sleep(0.05)
        emit('receive_poem_stream', {'poem_chunk': poem_chunk, 'emotions': emotion_data})
