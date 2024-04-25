from openai import OpenAI
from flask import Flask, request, jsonify, session
from flask_cors import CORS
import json

app = Flask(__name__)
CORS(app)


app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

with open('config.json', 'r') as f:
    config = json.load(f)
API_KEY = config['API_KEY']

openai = OpenAI(api_key=API_KEY)

@app.route('/')
def index():
    return 'Welcome to the Medical Health Assistant API with GPT-3 language model'

prompt = """You are an AI assistant that is an expert in medical health and is part of a hospital system called medical society system AI.
You know about symptoms and signs of various types of illnesses.
You can provide expert advice on self-diagnosis options in the case where an illness can be treated using a home remedy and suggest doctor's specialization.
If a query requires serious medical attention with a doctor, recommend them to book an appointment with our doctors.
If you are asked a question that is not related to medical health, respond with "I'm sorry but your question is beyond my functionalities".
Do not use external URLs or blogs to refer.
Format any lists on individual lines with a dash and a space in front of each line.
Try to make your answers small please and organized.
Additionally,suggest utilizing our device to measure heart rate and oxygen pulse.

"""

@app.route('/message', methods=['POST'])
def process_message():
    try:
        req_data = request.get_json()
        print("Request Data:", req_data) 
        user_id = req_data.get('user_id', None)
    
        if not user_id:
            return jsonify({'error': 'User ID is required'}), 400
        
    
        user_message = req_data['message']
        
        previous_messages = session.get(user_id, [])
        
        previous_messages.append(user_message)
        
        if len(previous_messages) > 5:
            previous_messages = previous_messages[-5:]
        
        session[user_id] = previous_messages
        
        context = "\n".join(previous_messages)
        
        prompt_with_context = prompt + context
        
        payload = {
            "messages": [{"role": "system", "content": prompt_with_context}, {"role": "user", "content": user_message}],
            "model": "gpt-3.5-turbo",
        }
        
        response = openai.chat.completions.create(**payload)
        
        ai_reply = response.choices[0].message.content
        
        message = {'message': ai_reply}
        
        return jsonify(message), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    app.run()
