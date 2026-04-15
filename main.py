import random
import logging
import os
import io
from threading import Thread
from http.server import BaseHTTPRequestHandler, HTTPServer
from gtts import gTTS
from telegram import ReplyKeyboardMarkup, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler

# --- RENDER ҮШІН ВЕБ-СЕРВЕР (ҚАТЕ ЖОЮ ҮШІН) ---
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is running")

def run_server():
    server = HTTPServer(('0.0.0.0', 10000), HealthCheckHandler)
    server.serve_forever()

# --- ЛОГИКА ЖӘНЕ БОТ ---
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
TOKEN = "8713961102:AAEjjLuLvXbea4xN3e7cbbxLQY1Ixddx0a8"

WORDS_DB = [
    {"word": "Environment", "phon": "[ɪnˈvaɪrənmənt]", "trans": "Қоршаған орта", "def": "The surroundings in which a person lives.", "ex": "Protect our environment.", "tf_q": "Does 'Environment' mean 'City'?", "tf_a": "false"},
    {"word": "Sustainable", "phon": "[səˈsteɪnəbl]", "trans": "Тұрақты", "def": "Able to continue without harming nature.", "ex": "Solar energy is sustainable.", "tf_q": "Is solar energy sustainable?", "tf_a": "true"},
    {"word": "Independent", "phon": "[ˌɪndɪˈpendənt]", "trans": "Тәуелсіз", "def": "Not controlled by others.", "ex": "Kazakhstan is independent.", "tf_q": "Is Kazakhstan an independent country?", "tf_a": "true"}
]

QUIZ_DB = [
    {"q": "What is the synonym of 'Huge'?", "o": ["A) Tiny", "B) Enormous", "C) Small"], "a": "B", "exp": "Enormous means extremely large."}
]

MENU = ReplyKeyboardMarkup([
    ["Learn Words 📚", "Quiz 🧠"], 
    ["Interactive Games 🎮", "Sentence ✍️"], 
    ["Listening 🎧", "True/False ✅"], 
    ["Game 🎮", "Help ❓"]
], resize_keyboard=True)

def get_unique_item(context, db, key):
    used_key = f"used_{key}"
    if used_key not in context.user_data or len(context.user_data[used_key]) >= len(db):
        context.user_data[used_key] = []
    available = [i for i in range(len(db)) if i not in context.user_data[used_key]]
    idx = random.choice(available)
    context.user_data[used_key].append(idx)
    return db[idx]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    await update.message.reply_text("👋 Welcome! Your English AI Tutor is ready.", reply_markup=MENU)

async def handle_logic(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text: return
    text = update.message.text.strip()
    state = context.user_data.get("state")

    if text == "Learn Words 📚":
        w = get_unique_item(context, WORDS_DB, "words")
        await update.message.reply_text(f"📚 *Word:* {w['word']}\n🇰🇿 *Аударма:* {w['trans']}", parse_mode="Markdown")
        return
    elif text == "Interactive Games 🎮":
        games_text = (
            "Interactive Games for practice:\n\n"
            "1. Family Members 👨‍👩‍👧‍👦:\nhttps://wordwall.net/resource/16223990\n"
            "2. Vocabulary Practice 📖:\nhttps://wordwall.net/resource/16581690\n"
            "3. Revision Game ⚡:\nhttps://wordwall.net/ru/resource/74390841"
        )
        await update.message.reply_text(games_text)
        return
    elif text == "Quiz 🧠":
        q = get_unique_item(context, QUIZ_DB, "quiz")
        context.user_data.update({"state": "QUIZ", "ans": q["a"], "exp": q["exp"]})
        await update.message.reply_text(f"🧠 {q['q']}\n" + "\n".join(q["o"]))
        return

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == context.user_data.get("tf_correct_ans"):
        await query.edit_message_text("✅ Correct!")
    else:
        await query.edit_message_text("❌ Wrong!")

if __name__ == '__main__':
    # ВЕБ-СЕРВЕРДІ ІСКЕ ҚОСУ
    Thread(target=run_server, daemon=True).start()
    
    app = ApplicationBuilder().token("8713961102:AAEJjLuLvXbea4xN3e7cbbxLQYlIxddxOa8").build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_logic))
    app.run_polling()
