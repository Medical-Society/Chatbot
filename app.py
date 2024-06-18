# from openai import AzureOpenAI

# # gets the API Key from environment variable AZURE_OPENAI_API_KEY
# client = AzureOpenAI(
#     # https://learn.microsoft.com/azure/ai-services/openai/reference#rest-api-versioning
#     api_version="2024-06-01",
#     api_key="ec35a3c78358449b90cf1f3a11884b0e",
#     # https://learn.microsoft.com/azure/cognitive-services/openai/how-to/create-resource?pivots=web-portal#create-a-resource
#     azure_endpoint="https://mssaichat.openai.azure.com/",
# )

# completion = client.chat.completions.create(
#     model="MSSChat", 
#     messages=[
#         {
#             "role": "user",
#             "content": "what is drugs in prescription : Rx maxicollin 30ml ",
#         },
#     ],
# )
# print(completion.choices[0].message.content)


from flask import Flask, request, jsonify
from openai import AzureOpenAI
import os
import re

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

# Configure the Azure OpenAI client
api_key = os.getenv('AZURE_OPENAI_API_KEY', 'ec35a3c78358449b90cf1f3a11884b0e')  # Replace with your API key if not using environment variable
azure_endpoint = "https://mssaichat.openai.azure.com/"

client = AzureOpenAI(
    api_version="2024-06-01",
    api_key=api_key,
    azure_endpoint=azure_endpoint
)

chat_sessions = {}

@app.route('/')
def index():
    return 'Welcome to the Medical Health Assistant API with Azure OpenAI language model'

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
        chat_sessions[user_id] = [{"role": "system", "content": prompt}]
    
    try:
        chat_history = chat_sessions[user_id]
        chat_history.append({"role": "user", "content": message})
        completion = client.chat.completions.create(
            model="MSSChat", 
            messages=chat_history,
        )
        response_text = format_response(completion.choices[0].message.content)
        chat_history.append({"role": "assistant", "content": response_text})
        chat_sessions[user_id] = chat_history
        return jsonify({"response": response_text})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run()
