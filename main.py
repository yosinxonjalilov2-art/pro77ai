import os
import threading
import requests
import urllib.parse
import telebot
from http.server import HTTPServer, BaseHTTPRequestHandler
from g4f.client import Client

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

# G4F AI Klientini ishga tushirish
ai_client = Client()

@bot.message_handler(commands=['start'])
def start_cmd(message):
    welcome_text = (
        "👋 **Pro 77 AI botiga xush kelibsiz!**\n\n"
        "🤖 **Matnli AI:** Menga istalgan savolingizni yozing, sun'iy intellekt javob beradi.\n\n"
        "🎨 **Rasm chizish:** Rasm yasash uchun `/image` buyrug'idan foydalaning.\n"
        "*(Masalan: `/image kosmosdagi uchayotgan mashina`)*"
    )
    bot.reply_to(message, welcome_text, parse_mode="Markdown")

# 1. RASM CHIZISH BO'LIMI (/image buyrug'i)
@bot.message_handler(commands=['image'])
def generate_image(message):
    prompt = message.text.replace('/image', '').strip()

    if not prompt:
        bot.reply_to(message, "⚠️ Nima rasm chizishim kerakligini yozing!\n\n**Misol:** `/image suv ostidagi shahar`", parse_mode="Markdown")
        return

    status_msg = bot.reply_to(message, "🎨 Rasm chizilmoqda, bir oz kuting (10-15 soniya)...")

    try:
        encoded_prompt = urllib.parse.quote(prompt)
        image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1024&height=1024&nologo=true"

        response = requests.get(image_url, timeout=60)

        if response.status_code == 200:
            bot.send_photo(
                message.chat.id, 
                response.content, 
                caption=f"🎨 **Siz so'ragan rasm:**\n_{prompt}_", 
                parse_mode="Markdown",
                reply_to_message_id=message.message_id
            )
            bot.delete_message(message.chat.id, status_msg.message_id)
        else:
            bot.edit_message_text("❌ Rasmni chizishda xatolik yuz berdi. Qaytadan urinib ko'ring.", chat_id=message.chat.id, message_id=status_msg.message_id)

    except Exception:
        bot.edit_message_text("❌ Rasm yaratishda vaqt tugadi yoki xatolik bo'ldi. Qayta urinib ko'ring.", chat_id=message.chat.id, message_id=status_msg.message_id)

# 2. AI CHAT BO'LIMI (GPT-4o orqali barqaror va o'zbekcha)
@bot.message_handler(func=lambda message: True)
def ai_chat(message):
    user_text = message.text.strip()
    bot.send_chat_action(message.chat.id, 'typing')

    try:
        response = ai_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "Siz foydali va aqlli sun'iy intellektsiz. Har doim o'zbek tilida aniq, tushunarli va chiroyli javob bering."},
                {"role": "user", "content": user_text}
            ]
        )

        reply_text = response.choices[0].message.content

        if reply_text:
            bot.reply_to(message, reply_text)
        else:
            bot.reply_to(message, "😔 Kechirasiz, javob tayyorlashda xatolik bo'ldi.")

    except Exception as e:
        bot.reply_to(message, "⚠️ Hozirda AI serverida yuklama yuqori. Birozdan so meymon qayta urinib ko'ring.")

if __name__ == "__main__":
    bot.infinity_polling(skip_pending=True)
