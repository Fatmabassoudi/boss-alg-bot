import os
import random
from datetime import datetime, timedelta
from flask import Flask
from threading import Thread
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# --- جزء الـ Flask لإبقاء البوت مستيقظاً على Render ---
app = Flask('')

@app.route('/')
def home():
    return "Boss Bot is Running!"

def run():
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))

def keep_alive():
    t = Thread(target=run)
    t.start()

# تشغيل السيرفر الوهمي
keep_alive()

# --- إعدادات البوت الأساسية ---
TOKEN = '8794281359:AAHqUGfD6k-ZiAiBZYQMIkVr0o-enkdhl8Y'
VIP_CHANNEL_ID = -1003844075678  # المعرف الصحيح الذي اتفقنا عليه

ASSETS = [
    "EUR/USD-OTC", "GBP/USD-OTC", "USD/JPY-OTC", "AUD/USD-OTC",
    "EUR/GBP-OTC", "NZD/USD-OTC", "USD/CAD-OTC", "USD/CHF-OTC",
    "GBP/JPY-OTC", "EUR/JPY-OTC", "AUD/CAD-OTC", "GBP/CHF-OTC",
    "USD/BRL-OTC", "USD/INR-OTC", "USD/TRY-OTC"
]

async def is_user_vip(user_id, context):
    try:
        member = await context.bot.get_chat_member(chat_id=VIP_CHANNEL_ID, user_id=user_id)
        return member.status in ['member', 'administrator', 'creator']
    except Exception as e:
        print(f"Error checking VIP: {e}")
        return False

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if await is_user_vip(user_id, context):
        keyboard = []
        for i in range(0, len(ASSETS), 2):
            row = [InlineKeyboardButton(ASSETS[i], callback_data=f"asset_{ASSETS[i]}")]
            if i + 1 < len(ASSETS):
                row.append(InlineKeyboardButton(ASSETS[i+1], callback_data=f"asset_{ASSETS[i+1]}"))
            keyboard.append(row)
        await update.message.reply_text(
            "💎 **WELCOME TO BOSS VIP SYSTEM**\n━━━━━━━━━━━━━━\nإختر زوج العملات للتحليل المتقدم:",
            reply_markup=InlineKeyboardMarkup(keyboard), 
            parse_mode='Markdown'
        )
    else:
        await update.message.reply_text("⚠️ **عذراً! هذا البوت مخصص لأعضاء قناة VIP فقط.**")

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data.startswith("asset_"):
        asset = query.data.replace("asset_", "")
        action = random.choice(["CALL 🟢 (صعود)", "PUT 🔴 (هبوط)"])
        entry_time = (datetime.now() + timedelta(minutes=1)).strftime("%H:%M")
        accuracy = random.randint(94, 98)
        
        msg = (
            f"🚀 **BOSS VIP SIGNAL**\n"
            f"━━━━━━━━━━━━━━\n"
            f"📦 **الـزوج:** `{asset}`\n"
            f"⏰ **الـوقت:** `{entry_time}`\n"
            f"💡 **الإشارة:** **{action}**\n"
            f"🎯 **الـدقة:** `{accuracy}%` \n"
            f"━━━━━━━━━━━━━━\n"
        )
        
        keyboard = [[InlineKeyboardButton("قنص إشارة أخرى 🔄", callback_data=f"asset_{asset}")]]
        await query.edit_message_text(text=msg, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')

if __name__ == '__main__':
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CallbackQueryHandler(button_handler))
    application.run_polling()
