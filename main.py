import random
import logging
import os
import io
from gtts import gTTS
from telegram import ReplyKeyboardMarkup, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler

# 1. Logging setup
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# 2. BOT TOKEN
TOKEN = "8713961102:AAEjjLuLvXbea4xN3e7cbbxLQY1Ixddx0a8"

# 3. DATABASE
WORDS_DB = [
    {"word": "Environment", "phon": "[ɪnˈvaɪrənmənt]", "trans": "Қоршаған орта", "def": "The surroundings in which a person lives.", "ex": "Protect our environment.", "tf_q": "Does 'Environment' mean 'City'?", "tf_a": "false"},
    {"word": "Sustainable", "phon": "[səˈsteɪnəbl]", "trans": "Тұрақты", "def": "Able to continue without harming nature.", "ex": "Solar energy is sustainable.", "tf_q": "Is solar energy sustainable?", "tf_a": "true"},
    {"word": "Independent", "phon": "[ˌɪndɪˈpendənt]", "trans": "Тәуелсіз", "def": "Not controlled by others.", "ex": "Kazakhstan is independent.", "tf_q": "Is Kazakhstan an independent country?", "tf_a": "true"},
    {"word": "Significant", "phon": "[sɪɡˈnɪfɪkənt]", "trans": "Маңызды", "def": "Having a great meaning.", "ex": "A significant discovery.", "tf_q": "Does 'Significant' mean 'Tiny'?", "tf_a": "false"},
    {"word": "Knowledge", "phon": "[ˈnɒlɪdʒ]", "trans": "Білім", "def": "Facts gained through experience.", "ex": "Knowledge is power.", "tf_q": "Is knowledge a power?", "tf_a": "true"}
]

QUIZ_DB = [
    {"q": "What is the synonym of 'Huge'?", "o": ["A) Tiny", "B) Enormous", "C) Small"], "a": "B", "exp": "Enormous means extremely large."},
    {"q": "Antonym of 'Success'?", "o": ["A) Failure", "B) Victory", "C) Win"], "a": "A", "exp": "Failure is the opposite of success."},
    {"q": "Which word means 'Very Old'?", "o": ["A) Modern", "B) Ancient", "C) New"], "a": "B", "exp": "Ancient refers to thousands of years ago."}
]

# 4. MENU
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
    await update.message.reply_text(
        "👋 Welcome! Your English AI Tutor is ready.\nChoose any game from the menu below:",
        reply_markup=MENU
    )

async def handle_logic(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return
        
    text = update.message.text.strip()
    state = context.user_data.get("state")

    # --- BUTTON COMMANDS ---
    if text == "Learn Words 📚":
        w = get_unique_item(context, WORDS_DB, "words")
        msg = f"📚 *Word:* {w['word']}\n🔊 *{w['phon']}*\n🇰🇿 *Аударма:* {w['trans']}\n📖 *Def:* {w['def']}\n📝 *Ex:* _{w['ex']}_"
        await update.message.reply_text(msg, parse_mode="Markdown")
        return

    elif text == "Interactive Games 🎮":
        games_text = (
            "Interactive Games for practice:\n\n"
            "1. Family Members 👨‍👩‍👧‍👦:\nhttps://wordwall.net/resource/16223990\n\n"
            "2. Vocabulary Practice 📖:\nhttps://wordwall.net/resource/16581690\n\n"
            "3. Revision Game ⚡:\nhttps://wordwall.net/ru/resource/74390841"
        )
        await update.message.reply_text(games_text)
        return

    elif text == "Quiz 🧠":
        q = get_unique_item(context, QUIZ_DB, "quiz")
        context.user_data.update({"state": "QUIZ", "ans": q["a"], "exp": q["exp"]})
        await update.message.reply_text(f"🧠 *Quiz Time!*\n\n{q['q']}\n\n" + "\n".join(q["o"]), parse_mode="Markdown")
        return

    elif text == "Game 🎮":
        word_obj = get_unique_item(context, WORDS_DB, "words")
        word = word_obj["word"].upper()
        shuffled = "".join(random.sample(word, len(word)))
        context.user_data.update({"state": "GAME", "ans": word})
        await update.message.reply_text(f"🎮 *Unscramble the word:* {shuffled}")
        return

    elif text == "Sentence ✍️":
        w = get_unique_item(context, WORDS_DB, "words")["word"]
        context.user_data.update({"state": "SENTENCE", "target": w})
        await update.message.reply_text(f"✍️ *Task:* Write a full sentence using: *{w}*", parse_mode="Markdown")
        return

    elif text == "Listening 🎧":
        w_obj = get_unique_item(context, WORDS_DB, "words")
        word = w_obj["word"]
        tts = gTTS(text=f"The word is {word}", lang='en')
        audio_stream = io.BytesIO()
        tts.write_to_fp(audio_stream)
        audio_stream.seek(0)
        context.user_data.update({"state": "LISTENING", "ans": word.upper()})
        await update.message.reply_voice(voice=audio_stream, caption="🎧 Listen and type the word:")
        return

    elif text == "True/False ✅":
        w = get_unique_item(context, WORDS_DB, "words")
        context.user_data.update({"tf_correct_ans": w['tf_a']})
        keyboard = [[InlineKeyboardButton("True ✅", callback_data="true"), 
                     InlineKeyboardButton("False ❌", callback_data="false")]]
        await update.message.reply_text(f"🧐 *True or False?*\n\n{w['tf_q']}", reply_markup=InlineKeyboardMarkup(keyboard))
        return

    # --- ANSWER CHECKING ---
    if state == "QUIZ":
        if text.upper().startswith(context.user_data.get("ans", "")):
            await update.message.reply_text("✅ *Correct!*", parse_mode="Markdown")
        else:
            await update.message.reply_text(f"❌ *Wrong.* Answer: {context.user_data.get('ans')}\n{context.user_data.get('exp')}", parse_mode="Markdown")
        context.user_data["state"] = None

    elif state in ["GAME", "LISTENING"]:
        if text.strip().upper() == context.user_data.get("ans", ""):
            await update.message.reply_text("🎯 *Perfect!* ✅")
        else:
            await update.message.reply_text(f"❌ *Incorrect.* It was: {context.user_data.get('ans')}")
        context.user_data["state"] = None

    elif state == "SENTENCE":
        target = context.user_data.get("target", "").lower()
        if target in text.lower() and len(text.split()) >= 3:
            await update.message.reply_text("🌟 *Great sentence!* ✅")
        else:
            await update.message.reply_text(f"⚠️ *Try again!* Use '{target}' in a sentence.")
        context.user_data["state"] = None

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    correct_ans = context.user_data.get("tf_correct_ans")
    if query.data == correct_ans:
        await query.edit_message_text(f"✅ *Correct!* You're right.", parse_mode="Markdown")
    else:
        await query.edit_message_text(f"❌ *Wrong!* Think again.", parse_mode="Markdown")

if __name__ == '__main__':
    app = ApplicationBuilder().token("8713961102:AAEJjLuLvXbea4xN3e7cbbxLQYlIxddxOa8").build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_logic))
    app.run_polling()
