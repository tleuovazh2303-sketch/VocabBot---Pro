import random
import logging
import os
import io
from flask import Flask
from threading import Thread
from gtts import gTTS
from telegram import ReplyKeyboardMarkup, Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# --- 1. RENDER ҮШІН ВЕБ-СЕРВЕР ---
app = Flask('')

@app.route('/')
def home():
    return "Bot is alive!"

def run_web():
    # Render талап ететін порт (10000)
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)

# --- 2. БОТ ЛОГИКАСЫ ---
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
TOKEN = "8713961102:AAEjjLuLvXbea4xN3e7cbbxLQY1Ixddx0a8"

WORDS_DB = [
    {"word": "Environment", "trans": "Қоршаған орта", "def": "The surroundings in which a person lives."},
    {"word": "Sustainable", "trans": "Тұрақты", "def": "Able to continue without harming nature."},
    {"word": "Independent", "trans": "Тәуелсіз", "def": "Not controlled by others."}
]

MENU = ReplyKeyboardMarkup([
    ["Learn Words 📚", "Quiz 🧠"], 
    ["Sentence ✍️", "Listening 🎧"], 
    ["Help ❓"]
], resize_keyboard=True)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Бот дайын! Мәзірден таңдаңыз:", reply_markup=MENU)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text == "Learn Words 📚":
        w = random.choice(WORDS_DB)
        await update.message.reply_text(f"📚 *Word:* {w['word']}\n🇰🇿 *Аударма:* {w['trans']}\n📖 *Def:* {w['def']}", parse_mode="Markdown")
    elif text == "Listening 🎧":
        w = random.choice(WORDS_DB)
        word = w["word"]
        tts = gTTS(text=f"The word is {word}", lang='en')
        audio = io.BytesIO()
        tts.write_to_fp(audio)
        audio.seek(0)
        await update.message.reply_voice(voice=audio, caption="🎧 Listen and repeat!")
    else:
        await update.message.reply_text("Таңдауыңызды түсінбедім, мәзірді қолданыңыз.")

if __name__ == '__main__':
    # Веб-серверді бөлек ағында іске қосу
    Thread(target=run_web, daemon=True).start()
    
    # Ботты іске қосу
    bot_app = ApplicationBuilder().token("8713961102:AAEJjLuLvXbea4xN3e7cbbxLQYlIxddxOa8").build()
    bot_app.add_handler(CommandHandler("start", start))
    bot_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("Бот іске қосылды...")
    bot_app.run_polling()
