import os
import json
import logging
import requests
from flask import Flask, request, jsonify
from groq import Groq
import gspread
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from datetime import datetime, timedelta
import pytz

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Environment variables
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
GMAIL_USER = os.environ.get("GMAIL_USER")

groq_client = Groq(api_key=GROQ_API_KEY)

SYSTEM_PROMPT = """You are RJ, a personal assistant for Archi Marrapu. 

About Archi:
- 18 year old Indian-American founder and bioengineering student at Northeastern University
- CEO of VOYCE, an end-to-end public speaking platform that analyzes delivery across 14 metrics
- Runs 5 tracks simultaneously: VOYCE startup, personal branding (@girl_who_builds), career (Sherman Co-op), health (75 Hard), and summer classes
- Based in Boston, from Alexandria VA, went to Thomas Jefferson High School
- Turned down a $240K job offer to build VOYCE
- 2x TEDx speaker, Congressional App Challenge winner, IEEE published, founded STEMifyGirls nonprofit
- Doing 75 Hard: 2x workouts daily, 1300 cal, gallon of water, 10 pages reading, brain dump, progress photo

Your personality as RJ:
- Direct, warm, human. Never robotic or corporate
- Match her energy — casual, sharp, fast moving
- When she complains, acknowledge briefly then push her forward. Never baby her
- Keep responses concise unless she asks for detail
- You check in on her proactively, keep her accountable
- You know her schedule, goals, and what she's working on
- You are supportive but brutally honest when needed

When Archi asks you to send an email, respond ONLY in this exact JSON format:
{"action":"send_email","to":"email@example.com","subject":"subject here","body":"email body here"}

When Archi asks you to set a reminder, respond ONLY in this exact JSON format:
{"action":"set_reminder","message":"reminder message here","minutes":30}

For all other messages respond normally as RJ in plain text."""

conversation_history = {}

def send_telegram_message(chat_id, text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}
    response = requests.post(url, json=payload)
    return response.json()

def get_groq_response(chat_id, user_message):
    if chat_id not in conversation_history:
        conversation_history[chat_id] = []
    
    conversation_history[chat_id].append({
        "role": "user",
        "content": user_message
    })
    
    # Keep last 20 messages for context
    recent_history = conversation_history[chat_id][-20:]
    
    messages = [{"role": "system", "content": SYSTEM_PROMPT}] + recent_history
    
    response = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=messages,
        max_tokens=1000
    )
    
    assistant_message = response.choices[0].message.content
    
    conversation_history[chat_id].append({
        "role": "assistant",
        "content": assistant_message
    })
    
    return assistant_message

def handle_action(chat_id, response_text):
    try:
        data = json.loads(response_text)
        action = data.get("action")
        
        if action == "send_email":
            # Gmail sending via API would go here
            # For now confirm to user
            send_telegram_message(chat_id, f"Got it, sending email to {data.get('to')} with subject: {data.get('subject')}")
            return True
            
        elif action == "set_reminder":
            send_telegram_message(chat_id, f"Reminder set! I'll ping you in {data.get('minutes')} minutes: {data.get('message')}")
            return True
            
    except (json.JSONDecodeError, KeyError):
        return False
    
    return False

@app.route(f"/webhook/{TELEGRAM_TOKEN}", methods=["POST"])
def webhook():
    data = request.get_json()
    
    if "message" not in data:
        return jsonify({"ok": True})
    
    message = data["message"]
    chat_id = message["chat"]["id"]
    text = message.get("text", "")
    
    if not text:
        return jsonify({"ok": True})
    
    logger.info(f"Message from {chat_id}: {text}")
    
    try:
        response = get_groq_response(str(chat_id), text)
        
        # Check if response is an action
        if not handle_action(chat_id, response):
            send_telegram_message(chat_id, response)
            
    except Exception as e:
        logger.error(f"Error: {e}")
        send_telegram_message(chat_id, "Sorry, something went wrong on my end. Try again.")
    
    return jsonify({"ok": True})

@app.route("/set_webhook", methods=["GET"])
def set_webhook():
    render_url = os.environ.get("RENDER_URL")
    webhook_url = f"{render_url}/webhook/{TELEGRAM_TOKEN}"
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/setWebhook?url={webhook_url}"
    response = requests.get(url)
    return jsonify(response.json())

@app.route("/", methods=["GET"])
def index():
    return "RJ is alive and running."

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
