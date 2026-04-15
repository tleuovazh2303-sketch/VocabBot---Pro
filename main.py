import random
import logging
import os
import io
from flask import Flask
from threading import Thread
from gtts import gTTS
from telegram import ReplyKeyboardMarkup, Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# --- 1. RENDER ҮШІН ВЕБ-СЕРВЕР (Health Check үшін) ---
web_app = Flask('')

@web_app.route('/')
def home():
    return "Bot is running"

def run_web():
    port = int(os.environ.get('PORT', 10000))
    web_app.run(host='0.0.0.0', port=port)

# --- 2. БОТ ЛОГИКАСЫ ---
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
TOKEN = "8713961102:AAEjjLuLvXbea4xN3e7cbbxLQY1Ixddx0a8"

# Wordwall-сыз деректер базасы
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
    await update.message.reply_text("👋 Сәлем! Бот дайын. Мәзірден таңдаңыз:", reply_markup=MENU)

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
        await update.message.reply_voice(voice=audio, caption="🎧 Listen carefully!")
    else:
        await update.message.reply_text("Төмендегі мәзірді қолданыңыз.")

if __name__ == '__main__':
    # 1. Веб-серверді бөлек ағында жіберу
    Thread(target=run_web, daemon=True).start()
    
    # 2. Telegram ботты іске қосу
    app = ApplicationBuilder().token("8713961102:AAEjjLuLvXbea4xN3e7cbbxLQY1Ixddx0a8").build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("Бот қосылды...")
    app.run_polling()
