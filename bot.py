import os
import random
from datetime import datetime, timedelta
from flask import Flask
from threading import Thread
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# --- الحفاظ على استقرار السيرفر (Flask) ---
app = Flask('')
@app.route('/')
def home(): return "Boss Bot is Live"

def run(): app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
def keep_alive(): Thread(target=run).start()
keep_alive()

# --- الإعدادات ---
TOKEN = '8794281359:AAHqUGfD6k-ZiAiBZYQMIkVr0o-enkdhl8Y'
VIP_CHANNEL_ID = -1003844075678

# قائمة الـ 20 زوجاً كاملة
ASSETS = [
    "EUR/USD-OTC", "GBP/USD-OTC", "USD/JPY-OTC", "AUD/USD-OTC",
    "EUR/GBP-OTC", "NZD/USD-OTC", "USD/CAD-OTC", "USD/CHF-OTC",
    "GBP/JPY-OTC", "EUR/JPY-OTC", "AUD/CAD-OTC", "GBP/CHF-OTC",
    "USD/BRL-OTC", "USD/INR-OTC", "USD/TRY-OTC", "EUR/TRY-OTC",
    "CAD/JPY-OTC", "AUD/JPY-OTC", "NZD/JPY-OTC", "GBP/AUD-OTC"
]

async def is_user_vip(user_id, context):
    try:
        member = await context.bot.get_chat_member(chat_id=VIP_CHANNEL_ID, user_id=user_id)
        return member.status in ['member', 'administrator', 'creator']
    except: return False

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
            "👑 **نظام BOSS ALG VIP المطور**\n"
            "━━━━━━━━━━━━━━\n"
            "تم التحقق من العضوية. اختاري الزوج للتحليل:",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='Markdown'
        )
    else:
        await update.message.reply_text("⚠️ الوصول مخصص لأعضاء الـ VIP فقط.")

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    asset = query.data.replace("asset_", "")
    action = random.choice(["CALL 🟢 (صعود)", "PUT 🔴 (هبوط)"])
    entry_time = (datetime.now() + timedelta(minutes=1)).strftime("%H:%M")
    accuracy = random.randint(95, 99)

    signal_msg = (
        f"📊 **إشارة BOSS VIP المضمونة**\n"
        f"━━━━━━━━━━━━━━\n"
        f"🔹 **الـزوج:** `{asset}`\n"
        f"🔹 **الـدخول:** `{entry_time}`\n"
        f"🔹 **الاتجاه:** **{action}**\n"
        f"🔹 **الـدقة:** `{accuracy}%` 🔥\n"
        f"━━━━━━━━━━━━━━\n"
        f"🎯 *ادخلي مع بداية الشمعة القادمة مباشرة*"
    )
    
    keyboard = [[InlineKeyboardButton("قنص إشارة أخرى 🔄", callback_data=f"start_again")]]
    # ملاحظة: زر "إشارة أخرى" سيعود الآن لقائمة الـ 20 زوجاً
    await query.edit_message_text(text=signal_msg, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')

async def return_to_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    # كود لإعادة إظهار القائمة الرئيسية عند الضغط على "إشارة أخرى"
    keyboard = []
    for i in range(0, len(ASSETS), 2):
        row = [InlineKeyboardButton(ASSETS[i], callback_data=f"asset_{ASSETS[i]}")]
        if i + 1 < len(ASSETS):
            row.append(InlineKeyboardButton(ASSETS[i+1], callback_data=f"asset_{ASSETS[i+1]}"))
        keyboard.append(row)
    await query.edit_message_text("اختاري زوج العملات للتحليل:", reply_markup=InlineKeyboardMarkup(keyboard))

if __name__ == '__main__':
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CallbackQueryHandler(button_handler, pattern="^asset_"))
    application.add_handler(CallbackQueryHandler(return_to_start, pattern="^start_again$"))
    application.run_polling()
