import os 
import json
import requests
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
from google.oauth2 import service_account
from google.cloud import dialogflow_v2 as dialogflow

# Load environment variables from .env file
load_dotenv()

# Set Google Cloud API
google_credentials_json = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
credentials_info = json.loads(google_credentials_json)
credentials = service_account.Credentials.from_service_account_info(credentials_info)
DIALOGFLOW_PROJECT_ID = os.getenv("DIALOGFLOW_PROJECT_ID")

# Set Weather API
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")
WEATHER_API_URL = "http://api.weatherstack.com/current"

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

# Route3: Dialogflow Webhook for Weather Query
@app.route('/webhook', methods=['POST'])
def webhook():
    req = request.get_json()
    intent_name = req.get("queryResult", {}).get("intent", {}).get("displayName")
    parameters = req.get("queryResult", {}).get("parameters", {})
    
    if intent_name == "WeatherQuery":
        city = parameters.get("geo-city")
        if not city:
            return jsonify({"fulfillmentText": "Which city do you want to check the weather in?"})
        
        weather_response = requests.get(WEATHER_API_URL, params={"access_key": WEATHER_API_KEY, "query": city})
        weather_data = weather_response.json()
        
        if "current" in weather_data:
            temperature = weather_data["current"].get("temperature")
            weather_desc = weather_data["current"].get("weather_descriptions", ["Unknown"])[0]
            response_text = f"The current weather in {city} is {weather_desc} with a temperature of {temperature}°C."
        else:
            response_text = "I'm sorry, I couldn't fetch the weather information at the moment."
        
        return jsonify({"fulfillmentText": response_text})
    
    if intent_name == "Greeting Messages":
        receiver = parameters.get("Gift_Receiver")
        greeting_message = parameters.get("Greeting")  # 获取祝福语

        # 如果没有提供收礼人或祝福语
        if not receiver:
            return jsonify({"fulfillmentText": "Who is the recipient of this greeting card?"})

        if not greeting_message:
            return jsonify({"fulfillmentText": "What message would you like to write on the card?"})

        # 保存用户输入的收礼人和祝福语到会话中，等待确认
        user_sessions[session_id] = {"waiting_for_confirmation": True, "receiver": receiver, "greeting_message": greeting_message}
        
        # 询问用户确认
        confirmation_text = f"Dear {receiver}, your message is: \"{greeting_message}\". Do you confirm? (y/n)"
        return jsonify({"fulfillmentText": confirmation_text})

    # 处理用户的确认输入（y/n）
    user_response = parameters.get("sys.any")  # 获取用户的 y 或 n

    # 如果用户确认
    if user_response and user_response.lower() == 'y':
        return jsonify({"fulfillmentText": f"Your greeting to {receiver} has been saved: '{greeting_message}'."})

    # 如果用户不确认，重新要求输入祝福语
    elif user_response and user_response.lower() == 'n':
        return jsonify({"fulfillmentText": "Please provide a new greeting message."})

    else:
        return jsonify({"fulfillmentText": "I didn't understand that. Please respond with 'y' or 'n'."})

    return jsonify({"fulfillmentText": "   I'm not sure how to handle that request."}) 


if __name__ == '__main__':
    app.run(debug=True)