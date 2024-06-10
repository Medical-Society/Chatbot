from flask import Flask, request, jsonify
import google.generativeai as genai
from uuid import uuid4
import re

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

# Configure the Google AI SDK
genai.configure(api_key="AIzaSyCjVPfXxpSS75Yj5l1jzY0HvBzhn66IO8E")

# Create the model
generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 64,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}

model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    generation_config=generation_config,
    # safety_settings = Adjust safety settings
    # See https://ai.google.dev/gemini-api/docs/safety-settings
)

chat_sessions = {}

@app.route('/')
def index():
    return 'Welcome to the Medical Health Assistant API with Geni language model'

prompt = """You are an AI assistant that is an expert in medical health and is part of a hospital system called Medical Society System AI.
You know about symptoms and signs of various types of illnesses.
You can provide expert advice on self-diagnosis options in the case where an illness can be treated using a home remedy and suggest doctor's specialization.
If a query requires serious medical attention with a doctor, recommend them to book an appointment with our doctors.
If you are asked a question that is not related to medical health, respond with "I'm sorry but your question is beyond my functionalities".
Do not use external URLs or blogs to refer.
Format any lists on individual lines with a dash and a space in front of each line.
Try to make your answers small and organized.
Additionally, suggest utilizing our device to measure heart rate and oxygen pulse.
"""

def format_response(text):
    """Format the response text to be organized."""
    # Format lists with dashes
    text = re.sub(r'\n(\s*-\s)', r'\n- ', text)
    # Ensure new lines for lists
    text = re.sub(r'(\d+\.\s)', r'\n\1', text)
    text = re.sub(r'(\n\s*-)', r'\n- ', text)
    # Normalize multiple new lines
    text = re.sub(r'\n{2,}', '\n\n', text)
    return text.strip()

@app.route('/message', methods=['POST'])
def generate_response():
    data = request.get_json()
    message = data.get('message')
    user_id = data.get('user_id')
    
    if not message:
        return jsonify({"error": "No message provided"}), 400
    
    if not user_id:
        return jsonify({"error": "No user ID provided"}), 400

    if user_id not in chat_sessions:
        chat_sessions[user_id] = model.start_chat(history=[{"role": "user", "parts": [{"text": prompt}]}])
    
    try:
        chat_session = chat_sessions[user_id]
        response = chat_session.send_message({"role": "user", "parts": [{"text": message}]})
        response_text = format_response(response.text)  
        return jsonify({"response": response_text})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run()
