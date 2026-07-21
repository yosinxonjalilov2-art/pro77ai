import os
import threading
import requests
import urllib.parse
import telebot
import json
import re
from http.server import HTTPServer, BaseHTTPRequestHandler

# Render o'chmasligi uchun dummy server
class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"OK - Bot is running")

def run_dummy_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(('0.0.0.0', port), SimpleHTTPRequestHandler)
    server.serve_forever()

threading.Thread(target=run_dummy_server, daemon=True).start()

# BOT_TOKEN O'RNIGA BOTFATHER BERGAN TOKENNI QO'YING:
BOT_TOKEN = "8989021358:AAF2uXLXO9F37hoNw6Eok4nH8jMj1vgPWjc"
bot = telebot.TeleBot(BOT_TOKEN)

# Google Translate funksiyasi
def translate_to_english(text):
    if not text:
        return ""
    if re.fullmatch(r'[a-zA-Z0-9\s\.,!?\'-]+', text):
        return text
    
    try:
        url = f"https://translate.googleapis.com/translate_a/single?client=gtx&sl=auto&tl=en&dt=t&q={urllib.parse.quote(text)}"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            translated_text = ""
            for item in result[0]:
                if item[0]:
                    translated_text += item[0]
            return translated_text
        return text
    except Exception:
        return text

@bot.message_handler(commands=['start'])
def start_cmd(message):
    welcome_text = (
        "👋 **Pro 77 AI botiga xush kelibsiz!**\n\n"
        "🤖 **Matnli AI:** Menga istalgan savolingizni yozing, sun'iy intellekt javob beradi.\n\n"
        "🎨 **Rasm chizish (FLUX Model):** Rasm yasash uchun `/image` buyrug'idan foydalaning.\n"
        "*(Masalan: `/image qizil rangli super car, kechki shahar fonida, ultra-realistik`)*"
    )
    bot.reply_to(message, welcome_text, parse_mode="Markdown")

# 1. RASM CHIZISH BO'LIMI (FLUX MODELI ORQALI - ANIQ VA SIFATLI)
@bot.message_handler(commands=['image'])
def generate_image(message):
    original_prompt = message.text.replace('/image', '').strip()

    if not original_prompt:
        bot.reply_to(message, "⚠️ Nima rasm chizishim kerakligini yozing!\n\n**Misol:** `/image suv ostidagi shahar`", parse_mode="Markdown")
        return

    status_msg = bot.reply_to(message, "🎨 FLUX AI yordamida o'ta aniq rasm chizilmoqda, kuting (10-15 soniya)...")

    # Matnni tarjima qilish
    english_prompt = translate_to_english(original_prompt)

    try:
        encoded_prompt = urllib.parse.quote(english_prompt)
        # Modelni flux ga o'tkazdik (u so'rovlarni juda aniq va realistik chizadi)
        image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?model=flux&width=1024&height=1024&nologo=true"

        response = requests.get(image_url, timeout=60)

        if response.status_code == 200:
            bot.send_photo(
                message.chat.id, 
                response.content, 
                caption=f"🎨 **Siz so'ragan rasm (FLUX AI):**\n_{original_prompt}_\n\n*(Inglizcha tarjimasi: {english_prompt})*", 
                parse_mode="Markdown",
                reply_to_message_id=message.message_id
            )
            bot.delete_message(message.chat.id, status_msg.message_id)
        else:
            bot.edit_message_text("❌ Rasmni chizishda xatolik yuz berdi. Qaytadan urinib ko'ring.", chat_id=message.chat.id, message_id=status_msg.message_id)

    except Exception:
        bot.edit_message_text("❌ Rasm yaratishda vaqt tugadi yoki xatolik bo'ldi. Qayta urinib ko'ring.", chat_id=message.chat.id, message_id=status_msg.message_id)

# 2. AI CHAT BO'LIMI
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

        if response.status_code == 200 and response.text.strip():
            bot.reply_to(message, response.text)
        else:
            bot.reply_to(message, "😔 Kechirasiz, tarmoqda xatolik bo'ldi. Birozdan so'ng qayta urinib ko'ring.")

    except Exception:
        bot.reply_to(message, "⚠️ Server bilan bog'lanishda xatolik bo'ldi. Qaytadan urinib ko'ring.")

if __name__ == "__main__":
    bot.infinity_polling(skip_pending=True)
