import random
import logging
import os
import io
from flask import Flask
from threading import Thread
from gtts import gTTS
from telegram import ReplyKeyboardMarkup, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler

# --- 1. RENDER ҮШІН ВЕБ-СЕРВЕР ---
server = Flask('')

@server.route('/')
def home():
    return "Bot is running!"

def run_web_server():
    # Render беретін портты қолдану (әйтпесе 10000)
    port = int(os.environ.get('PORT', 10000))
    server.run(host='0.0.0.0', port=port)

# --- 2. БОТ ПАРАМЕТРЛЕРІ ---
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
TOKEN = "8713961102:AAEjjLuLvXbea4xN3e7cbbxLQY1Ixddx0a8"

# Деректер базасы (Wordwall-сыз тек ішкі ойындар)
WORDS_DB = [
    {"word": "Environment", "phon": "[ɪnˈvaɪrənmənt]", "trans": "Қоршаған орта", "def": "The surroundings in which a person lives.", "ex": "Protect our environment.", "tf_q": "Does 'Environment' mean 'City'?", "tf_a": "false"},
    {"word": "Sustainable", "phon": "[səˈsteɪnəbl]", "trans": "Тұрақты", "def": "Able to continue without harming nature.", "ex": "Solar energy is sustainable.", "tf_q": "Is solar energy sustainable?", "tf_a": "true"},
    {"word": "Independent", "phon": "[ˌɪndɪˈpendənt]", "trans": "Тәуелсіз", "def": "Not controlled by others.", "ex": "Kazakhstan is independent.", "tf_q": "Is Kazakhstan an independent country?", "tf_a": "true"}
]

QUIZ_DB = [
    {"q": "What is the synonym of 'Huge'?", "o": ["A) Tiny", "B) Enormous", "C) Small"], "a": "B", "exp": "Enormous means extremely large."}
]

# Мәзірден "Interactive Games" батырмасын алып тастадық
MENU = ReplyKeyboardMarkup([
    ["Learn Words 📚", "Quiz 🧠"], 
    ["Sentence ✍️", "Listening 🎧"], 
    ["True/False ✅", "Game 🎮"]
], resize_keyboard=True)

# Кездейсоқ элемент алу функциясы
def get_random_item(context, db, key):
    used_key = f"used_{key}"
    if used_key not in context.user_data or len(context.user_data[used_key]) >= len(db):
        context.user_data[used_key] = []
    available = [i for i in range(len(db)) if i not in context.user_data[used_key]]
    idx = random.choice(available)
    context.user_data[used_key].append(idx)
    return db[idx]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Сәлем! Ағылшын тілін үйрену боты дайын.", reply_markup=MENU)

async def handle_logic(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text: return
    text = update.message.text.strip()
    state = context.user_data.get("state")

    if text == "Learn Words 📚":
        w = get_random_item(context, WORDS_DB, "words")
        msg = f"📚 *Word:* {w['word']}\n🇰🇿 *Аударма:* {w['trans']}\n📖 *Def:* {w['def']}"
        await update.message.reply_text(msg, parse_mode="Markdown")
        return

    elif text == "Quiz 🧠":
        q = get_random_item(context, QUIZ_DB, "quiz")
        context.user_data.update({"state": "QUIZ", "ans": q["a"], "exp": q["exp"]})
        await update.message.reply_text(f"🧠 *Quiz:* {q['q']}\n\n" + "\n".join(q["o"]), parse_mode="Markdown")
        return

    elif text == "Listening 🎧":
        w_obj = get_random_item(context, WORDS_DB, "words")
        word = w_obj["word"]
        tts = gTTS(text=f"The word is {word}", lang='en')
        audio_stream = io.BytesIO()
        tts.write_to_fp(audio_stream)
        audio_stream.seek(0)
        context.user_data.update({"state": "LISTENING", "ans": word.upper()})
        await update.message.reply_voice(voice=audio_stream, caption="🎧 Сөзді тыңдап, жазыңыз:")
        return

    # Жауаптарды тексеру логикасы
    if state == "QUIZ":
        if text.upper().startswith(context.user_data.get("ans", "")):
            await update.message.reply_text("✅ Дұрыс!")
        else:
            await update.message.reply_text(f"❌ Қате. Жауап: {context.user_data.get('ans')}")
        context.user_data["state"] = None
    elif state == "LISTENING":
        if text.strip().upper() == context.user_data.get("ans"):
            await update.message.reply_text("🎯 Керемет! Дұрыс.")
        else:
            await update.message.reply_text(f"❌ Қате. Сөз: {context.user_data.get('ans')}")
        context.user_data["state"] = None

if __name__ == '__main__':
    # 1. Веб-серверді іске қосу (Render үшін)
    Thread(target=run_web_server, daemon=True).start()
    
    # 2. Ботты іске қосу
    app = ApplicationBuilder().token("8713961102:AAEJjLuLvXbea4xN3e7cbbxLQYlIxddxOa8").build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_logic))
    app.run_polling()
