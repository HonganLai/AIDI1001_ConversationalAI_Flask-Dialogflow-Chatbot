import os
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
from google.cloud import dialogflow_v2 as dialogflow

# Load environment variables from .env file
load_dotenv()
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")  # 设置 Google Cloud API 凭证路径
DIALOGFLOW_PROJECT_ID = os.getenv("DIALOGFLOW_PROJECT_ID")

app = Flask(__name__)

# Home page
@app.route('/')
def home():
    return render_template('index.html')

# Route1: student number
@app.route('/StudentNumber')
def student_number():
    STUDENT_NUMBER = os.getenv("DIALOGFLOW_PROJECT_ID")
    if STUDENT_NUMBER:
        student_data = {"student_number": STUDENT_NUMBER}
        return jsonify(student_data)
    else:
        return jsonify({"error": "Student number not found"}), 400

# Route2: Dialogflow API
@app.route('/detectIntent', methods=['POST'])
def detect_intent():
    message = request.json.get('message', '')
    session_client = dialogflow.SessionsClient()
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
        return jsonify({"reply": "Sorry, I didn't understand that."}), 500  # 出错时返回通用错误信息

if __name__ == '__main__':
    app.run(debug=True)