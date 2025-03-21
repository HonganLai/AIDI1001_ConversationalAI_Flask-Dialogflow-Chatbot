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
    print("Webhook request received!")  # 打印调试信息到Heroku日志中
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
            icon_url = f"https://www.weatherstack.com/images/weather-icons/{weather_data['current'].get('weather_icons', ['default.png'])[0]}"
            
            # 构建卡片响应
            card_response = { 
                "fulfillmentMessages": [
                    {
                        "card": {
                            "title": f"Weather in {city}",
                            "subtitle": weather_desc,
                            "imageUri": icon_url,  # 图标 URL
                            "buttons": [
                                {
                                    "text": "More details",
                                    "postback": "https://example.com/weather-details"
                                }
                            ]
                        }
                    },
                    {
                        "text": {
                            "text": [f"The temperature is {temperature}°C."]
                        }
                    }
                ]
            }
            
            return jsonify(card_response)
        else:
            response_text = "I'm sorry, I couldn't fetch the weather information at the moment."
            return jsonify({"fulfillmentText": response_text})
    
    return jsonify({"fulfillmentText": "I'm not sure how to handle that request."})

if __name__ == '__main__':
    app.run(debug=True)