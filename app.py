import os
import json
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
from google.oauth2 import service_account
from google.cloud import dialogflow_v2 as dialogflow

# Load environment variables from .env file
load_dotenv()

# Set Google Cloud API credentials using environment variable (from Heroku's config)
google_credentials_json = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

# Parse the credentials JSON string from the environment variable
credentials_info = json.loads(google_credentials_json)
credentials = service_account.Credentials.from_service_account_info(credentials_info)

DIALOGFLOW_PROJECT_ID = os.getenv("DIALOGFLOW_PROJECT_ID")

app = Flask(__name__)

# Home page
@app.route('/')
def home():
    return render_template('index.html')

# Route1: student number
@app.route('/StudentNumber')
def student_number():
    STUDENT_NUMBER = os.getenv("STUDENT_NUMBER")
    if STUDENT_NUMBER:
        student_data = {"student_number": STUDENT_NUMBER}
        return jsonify(student_data)
    else:
        return jsonify({"error": "Student number not found"}), 400

# Route2: Dialogflow API
@app.route('/detectIntent', methods=['POST'])
def detect_intent():
    message = request.json.get('message', '')
    session_client = dialogflow.SessionsClient(credentials=credentials)
    session_id = "unique-session-id"
    session_path = f"projects/{DIALOGFLOW_PROJECT_ID}/agent/sessions/{session_id}"
    text_input = dialogflow.TextInput(text=message, language_code="en")
    query_input = dialogflow.QueryInput(text=text_input)

    try:
        response = session_client.detect_intent(request={"session": session_path, "query_input": query_input})
        reply = response.query_result.fulfillment_text
        return jsonify({"reply": reply})
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"reply": "Sorry, I didn't understand that."}), 500

if __name__ == '__main__':
    app.run(debug=True)