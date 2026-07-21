import os
import threading
import requests
import urllib.parse
import telebot
import re
from http.server import HTTPServer, BaseHTTPRequestHandler

# Dummy Server
class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"OK")

def run_dummy_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(('0.0.0.0', port), SimpleHTTPRequestHandler)
    server.serve_forever()

threading.Thread(target=run_dummy_server, daemon=True).start()

# TOKENLARNI YOZING:
BOT_TOKEN = "8989021358:AAF2uXLXO9F37hoNw6Eok4nH8jMj1vgPWjc"
HF_TOKEN = "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"  # hf_... deb boshlanadigan token

bot = telebot.TeleBot(BOT_TOKEN)

# Google Translate
def translate_to_english(text):
    if not text:
        return ""
    if re.fullmatch(r'[a-zA-Z0-9\s\.,!?\'-]+', text):
        return text
    try:
        url = f"https://translate.googleapis.com/translate_a/single?client=gtx&sl=auto&tl=en&dt=t&q={urllib.parse.quote(text)}"
        res = requests.get(url, timeout=10)
        if res.status_code == 200:
            result = res.json()
            translated = ""
            for item in result[0]:
                if item[0]:
                    translated += item[0]
            return translated
        return text
    except Exception:
        return text

# Hugging Face FLUX.1-schnell modeliga ulanish
def query_hf_flux(prompt):
    API_URL = "https://api-inference.huggingface.co/models/black-forest-labs/FLUX.1-schnell"
    headers = {"Authorization": f"Bearer {HF_TOKEN}"}
    payload = {"inputs": prompt}
    response = requests.post(API_URL, headers=headers, json=payload, timeout=60)
    return response

@bot.message_handler(commands=['start'])
def start_cmd(message):
    welcome_text = (
        "👋 **Pro 77 AI botiga xush kelibsiz!**\n\n"
        "🤖 **Matnli AI:** Menga istalgan savolingizni yozing.\n\n"
        "🎨 **Rasm chizish (FLUX.1):** Rasm yasash uchun `/image` buyrug'idan foydalaning.\n"
        "*(Masalan: `/image qizil rangli mashina suv ostida`)*"
    )
    bot.reply_to(message, welcome_text, parse_mode="Markdown")

# RASM CHIZISH BO'LIMI
@bot.message_handler(commands=['image'])
def generate_image(message):
    original_prompt = message.text.replace('/image', '').strip()

    if not original_prompt:
        bot.reply_to(message, "⚠️ Nima rasm chizishim kerakligini yozing!\n\n**Misol:** `/image suv ostidagi shahar`", parse_mode="Markdown")
        return

    status_msg = bot.reply_to(message, "🎨 HQ FLUX AI rasm chizmoqda, biroz kuting (10-20 soniya)...")

    english_prompt = translate_to_english(original_prompt)

    try:
        response = query_hf_flux(english_prompt)

        if response.status_code == 200:
            bot.send_photo(
                message.chat.id, 
                response.content, 
                caption=f"🎨 **Siz so'ragan rasm:**\n_{original_prompt}_", 
                parse_mode="Markdown",
                reply_to_message_id=message.message_id
            )
            bot.delete_message(message.chat.id, status_msg.message_id)
        else:
            bot.edit_message_text("❌ Server hozir band yoki API tokenda xatolik bor. Qayta urinib ko'ring.", chat_id=message.chat.id, message_id=status_msg.message_id)

    except Exception:
        bot.edit_message_text("❌ Rasm yaratishda vaqt tugadi. Qayta urinib ko'ring.", chat_id=message.chat.id, message_id=status_msg.message_id)

# AI CHAT BO'LIMI
@bot.message_handler(func=lambda message: True)
def ai_chat(message):
    user_text = message.text.strip()
    bot.send_chat_action(message.chat.id, 'typing')

    try:
        url = "https://text.pollinations.ai/openai"
        payload = {
            "messages": [
                {"role": "system", "content": "You are a helpful assistant. Always respond in Uzbek language accurately and clearly."},
                {"role": "user", "content": user_text}
            ],
            "model": "openai"
        }
        response = requests.post(url, json=payload, timeout=30)

        if response.status_
