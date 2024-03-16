from openai import OpenAI
from flask import Flask, request, jsonify , session
from flask_cors import CORS
import json , os

app = Flask(__name__)
CORS(app)

with open('Chatbot\config.json', 'r') as f:
    config = json.load(f)
API_KEY = config['API_KEY']

openai = OpenAI(api_key=API_KEY)

@app.route('/')
def index():
    return 'Welcome to the Medical Health Assistant API with GPT-3 language model'

prompt = """You are an AI assistant that is an expert in medical health and is part of a hospital system called medical society system AI
You know about symptoms and signs of various types of illnesses.
You can provide expert advice on self diagnosis options in the case where an illness can be treated using a home remedy.
if a query requires serious medical attention with a doctor, recommend them to book an appointment with our doctors
If you are asked a question that is not related to medical health respond with "Im sorry but your question is beyond my functionalities".
do not use external URLs or blogs to refer
Format any lists on individual lines with a dash and a space in front of each line.
try to make your answers small please and organized
"""

user_reply = ""
Ai_reply = ""
previous_messages = []
@app.route('/message', methods=['POST'])
def process_message():
    try:
        req_data = request.get_json()
        print("Request Data:", req_data) 
        
        previous_messages.append(req_data['message'])
       
        context = "\n".join(previous_messages)
        
      
        prompt_with_context = prompt + context
        
        payload = {
            "messages": [{"role": "system", "content": prompt_with_context}, {"role": "user", "content": req_data['message']}],
            "model": "gpt-3.5-turbo",
        }
        
        response = openai.chat.completions.create(**payload)
        
        message_content = response.choices[0].message.content
        
        message = {'message': message_content}
        
        return jsonify(message) , 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    app.run()