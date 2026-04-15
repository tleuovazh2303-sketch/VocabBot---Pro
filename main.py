import random
import logging
import os
from flask import Flask
from threading import Thread
from gtts import gTTS
import io
from telegram import ReplyKeyboardMarkup, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler

# 1. RENDER ҮШІН ВЕБ-СЕРВЕР (HEALTH CHECK)
server = Flask('')

@server.route('/')
def home():
    return "Bot is alive!"

def run():
    # Render әдетте 10000 портын қолданады
    server.run(host='0.0.0.0', port=int(os.environ.get('PORT', 10000)))

# 2. БОТ ЛОГИКАСЫ
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
TOKEN = "8713961102:AAEjjLuLvXbea4xN3e7cbbxLQY1Ixddx0a8"

WORDS_DB = [
    {"word": "Environment", "phon": "[ɪnˈvaɪrənmənt]", "trans": "Қоршаған орта", "def": "The surroundings in which a person lives.", "ex": "Protect our environment.", "tf_q": "Does 'Environment' mean 'City'?", "tf_a": "false"},
    {"word": "Sustainable", "phon": "[səˈsteɪnəbl]", "trans": "Тұрақты", "def": "Able to continue without harming nature.", "ex": "Solar energy is sustainable.", "tf_q": "Is solar energy sustainable?", "tf_a": "true"},
    {"word": "Independent", "phon": "[ˌɪndɪˈpendənt]", "trans": "Тәуелсіз", "def": "Not controlled by others.", "ex": "Kazakhstan is independent.", "tf_q": "Is Kazakhstan an independent country?", "tf_a": "true"}
]

MENU = ReplyKeyboardMarkup([
    ["Learn Words 📚", "Quiz 🧠"], 
    ["Interactive Games 🎮", "Sentence ✍️"], 
    ["Listening 🎧", "True/False ✅"]
], resize_keyboard=True)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Welcome! Your English AI Tutor is ready.", reply_markup=MENU)

async def handle_logic(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text == "Interactive Games 🎮":
        games_text = (
            "Interactive Games for practice:\n\n"
            "1. Family: https://wordwall.net/resource/16223990\n"
            "2. Vocab: https://wordwall.net/resource/16581690\n"
            "3. Revision: https://wordwall.net/ru/resource/74390841"
        )
        await update.message.reply_text(games_text)
    elif text == "Learn Words 📚":
        w = random.choice(WORDS_DB)
        await update.message.reply_text(f"📚 *Word:* {w['word']}\n🇰🇿 *Аударма:* {w['trans']}", parse_mode="Markdown")

if __name__ == '__main__':
    # Веб-серверді бөлек ағында іске қосу
    t = Thread(target=run)
    t.start()
    
    # Ботты іске қосу
    app = ApplicationBuilder().token("8713961102:AAEJjLuLvXbea4xN3e7cbbxLQYlIxddxOa8").build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_logic))
    app.run_polling()
