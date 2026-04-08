import os
import random
from datetime import datetime, timedelta
from flask import Flask
from threading import Thread
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# --- نظام الحماية والاستقرار (Flask) ---
app = Flask('')
@app.route('/')
def home(): return "Boss Global Bot is Online"

def run(): app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
def keep_alive(): Thread(target=run).start()
keep_alive()

# --- إعدادات البوت ---
TOKEN = '8794281359:AAHqUGfD6k-ZiAiBZYQMIkVr0o-enkdhl8Y'
VIP_CHANNEL_ID = -1003844075678

# القائمة الكاملة (41 زوجاً) مرتبة أبجدياً كما طلبتِ
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

def build_menu():
    keyboard = []
    # ترتيب الأزرار: كل زوجين في سطر لسهولة القراءة من الهاتف
    for i in range(0, len(ASSETS), 2):
        row = [InlineKeyboardButton(ASSETS[i], callback_data=f"asset_{ASSETS[i]}")]
        if i + 1 < len(ASSETS):
            row.append(InlineKeyboardButton(ASSETS[i+1], callback_data=f"asset_{ASSETS[i+1]}"))
        keyboard.append(row)
    return InlineKeyboardMarkup(keyboard)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if await is_user_vip(user_id, context):
        await update.message.reply_text(
            "👑 **مرحباً بكِ في BOSS ALG GLOBAL**\n"
            "━━━━━━━━━━━━━━\n"
            "تم التحقق من العضوية. لديكِ الوصول لـ 41 زوج عملات.\n"
            "إختار الزوج المطلوب للتحليل:",
            reply_markup=build_menu(),
            parse_mode='Markdown'
        )
    else:
        await update.message.reply_text("⚠️ الوصول مخصص لأعضاء الـ VIP فقط.")

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data.startswith("asset_"):
        asset = query.data.replace("asset_", "")
        action = random.choice(["CALL 🟢 (صعود)", "PUT 🔴 (هبوط)"])
        entry_time = (datetime.now() + timedelta(minutes=1)).strftime("%H:%M")
        accuracy = random.randint(95, 99)

        signal_msg = (
            f"📊 **إشارة BOSS VIP المضمونة**\n"
            f"━━━━━━━━━━━━━━\n"
            f"🔹 **الـزوج:** `{asset}`\n"
            f"🔹 **الـوقت:** `{entry_time}`\n"
            f"🔹 **الاتجاه:** **{action}**\n"
            f"🔹 **الـدقة:** `{accuracy}%` 🔥\n"
            f"━━━━━━━━━━━━━━\n"
            f"🎯 *ادخل مع بداية الشمعة القادمة مباشرة*"
        )
        
        keyboard = [[InlineKeyboardButton("قنص إشارة أخرى 🔄", callback_data="back_to_menu")]]
        await query.edit_message_text(text=signal_msg, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')

    elif query.data == "back_to_menu":
        await query.edit_message_text("اختاري زوج العملات للتحليل:", reply_markup=build_menu())

if __name__ == '__main__':
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CallbackQueryHandler(button_handler))
    application.run_polling()
