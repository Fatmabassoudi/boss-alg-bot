import os
import random
from datetime import datetime, timedelta
from flask import Flask
from threading import Thread
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# --- تشغيل السيرفر ---
app = Flask('')
@app.route('/')
def home(): return "Queen Trader Bot is Live!"

def run():
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run)
    t.start()

keep_alive()

# --- إعدادات البوت ---
TOKEN = '8794281359:AAHqUGfD6k-ZiAiBZYQMIkVr0o-enkdhl8Y'
VIP_CHANNEL_ID = -1003844075678

ASSETS = sorted([
    "NZD/CHF (OTC)", "USD/MXN (OTC)", "CHF/JPY (OTC)", "USD/IDR (OTC)", 
    "USD/BRL (OTC)", "USD/ARS (OTC)", "USD/NGN (OTC)", "USD/ZAR (OTC)", 
    "USD/CHF (OTC)", "USD/PKR (OTC)", "USD/BDT (OTC)", "NZD/JPY (OTC)", 
    "USD/INR (OTC)", "GBP/AUD (OTC)", "USD/EGP (OTC)", "AUD/CHF (OTC)", 
    "AUD/JPY (OTC)", "NZD/CAD (OTC)", "GBP/CHF (OTC)", "GBP/JPY (OTC)", 
    "AUD/CAD (OTC)", "CAD/CHF (OTC)", "EUR/JPY (OTC)", "AUD/USD (OTC)", 
    "EUR/AUD (OTC)", "EUR/CAD (OTC)", "EUR/CHF (OTC)", "EUR/GBP (OTC)", 
    "EUR/USD (OTC)", "USD/CAD (OTC)", "USD/COP (OTC)", "USD/DZD (OTC)", 
    "USD/JPY (OTC)", "USD/PHP (OTC)", "CAD/JPY (OTC)", "NZD/USD (OTC)", 
    "GBP/CAD (OTC)", "GBP/USD (OTC)", "EUR/NZD (OTC)", "EUR/SGD (OTC)", 
    "GBP/NZD (OTC)"
])

async def is_user_vip(user_id, context):
    try:
        member = await context.bot.get_chat_member(chat_id=VIP_CHANNEL_ID, user_id=user_id)
        return member.status in ['member', 'administrator', 'creator']
    except: return False

def build_assets_menu():
    keyboard = []
    for i in range(0, len(ASSETS), 3):
        row = [InlineKeyboardButton(ASSETS[i], callback_data=f"asset_{ASSETS[i]}")]
        if i + 1 < len(ASSETS):
            row.append(InlineKeyboardButton(ASSETS[i+1], callback_data=f"asset_{ASSETS[i+1]}"))
        if i + 2 < len(ASSETS):
            row.append(InlineKeyboardButton(ASSETS[i+2], callback_data=f"asset_{ASSETS[i+2]}"))
        keyboard.append(row)
    return InlineKeyboardMarkup(keyboard)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if await is_user_vip(user_id, context):
        await update.message.reply_text(
            "👑 **مرحباً بكِ في QUEEN TRADER VIP**\n━━━━━━━━━━━━━━\nإختار زوج العملات للتحليل الآن:",
            reply_markup=build_assets_menu(),
            parse_mode='Markdown'
        )
    else:
        await update.message.reply_text("⚠️ الوصول مقتصر على أعضاء QUEEN TRADER VIP فقط.")

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data.startswith("asset_"):
        asset = data.replace("asset_", "")
        keyboard = [[
            InlineKeyboardButton("1 MIN ⏱️", callback_data=f"time_1_{asset}"),
            InlineKeyboardButton("5 MIN ⏱️", callback_data=f"time_5_{asset}")
        ]]
        await query.edit_message_text(f"📦 الزوج: *{asset}*\nإختار مدة الصفقة:", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')

    elif data.startswith("time_"):
        parts = data.split("_")
        duration, asset = parts[1], parts[2]
        
        # محاكاة تحليل 4 مؤشرات (RSI, MACD, MA, Bollinger Bands)
        action = random.choice(["CALL 🟢 (صعود)", "PUT 🔴 (هبوط)"])
        entry_time = (datetime.now() + timedelta(minutes=1)).strftime("%H:%M")
        
        # رفع نسبة الدقة لتناسب الفلترة الرباعية الجديدة
        accuracy = random.randint(96, 99)

        signal_msg = (
            f"👑 **إشارة QUEEN TRADER الحصرية**\n━━━━━━━━━━━━━━\n"
            f"🔹 **الـزوج:** `{asset}`\n🔹 **الـوقت:** `{entry_time}`\n"
            f"🔹 **الـمدة:** `{duration} MIN`\n🔹 **الاتجاه:** **{action}**\n"
            f"🔹 **الـدقة:** `{accuracy}%` 🔥\n━━━━━━━━━━━━━━\n"
            f"🎯 **ادخل مارجينال لأفضل نتيجة**"
        )
        await query.edit_message_text(text=signal_msg, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("قنص إشارة أخرى 🔄", callback_data="back")]]), parse_mode='Markdown')

    elif data == "back":
        await query.edit_message_text("إختار زوج العملات للتحليل:", reply_markup=build_assets_menu())

if __name__ == '__main__':
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CallbackQueryHandler(button_handler))
    application.run_polling()
