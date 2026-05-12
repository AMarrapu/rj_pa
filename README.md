# RJ — Personal Assistant Bot

## Setup

### 1. Add these files to your GitHub repo
- main.py
- requirements.txt
- Procfile

### 2. Set environment variables in Render
Go to your Render service → Environment → Add the following:

| Key | Value |
|-----|-------|
| TELEGRAM_TOKEN | your telegram bot token |
| GROQ_API_KEY | your groq api key |
| RENDER_URL | your render app URL (e.g. https://rj-pa.onrender.com) |
| GMAIL_USER | your gmail address |

### 3. Deploy on Render
- Build Command: `pip install -r requirements.txt`
- Start Command: `gunicorn main:app`

### 4. Set the Telegram Webhook
Once deployed, visit:
`https://your-render-url.onrender.com/set_webhook`

That connects Telegram to RJ permanently.

### 5. Text RJ
Open Telegram, find @RJthePA_bot and start talking.

## What RJ can do
- Respond to any message as your personal assistant
- Remember conversation context
- Send emails (say "email [person] about [topic]")
- Set reminders (say "remind me in 30 minutes to...")
- More integrations coming soon
