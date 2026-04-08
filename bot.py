import http.server
import socketserver
import threading
import os
import random
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# --- خدعة السيرفر ليعمل Render مجاناً ---
def run_dummy_server():
    port = int(os.environ.get("PORT", 8080))
    handler = http.server.SimpleHTTPRequestHandler
    with socketserver.TCPServer(("", port), handler) as httpd:
        httpd.serve_forever()

threading.Thread(target=run_dummy_server, daemon=True).start()

# --- إعدادات البوت ---
TOKEN = '8794281359:AAHqUGfD6k-ZiAiBZYQMIkVr0o-enkdhl8Y'
VIP_CHANNEL_ID = '@1003844075678' # 👈 ضعي معرف قناتك هنا

ASSETS = [
    "EUR/USD-OTC", "GBP/USD-OTC", "USD/JPY-OTC", "AUD/USD-OTC",
    "EUR/GBP-OTC", "NZD/USD-OTC", "USD/CAD-OTC", "USD/CHF-OTC",
    "GBP/JPY-OTC", "EUR/JPY-OTC", "AUD/CAD-OTC", "GBP/CHF-OTC"
]

# دالة التحقق من الاشتراك
async def is_user_vip(user_id, context):
    try:
        member = await context.bot.get_chat_member(chat_id=VIP_CHANNEL_ID, user_id=user_id)
        if member.status in ['member', 'administrator', 'creator']:
            return True
        return False
    except:
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
        await update.message.reply_text("💎 **نظام BOSS VIP جاهز**\nاختر الزوج:", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')
    else:
        join_button = [[InlineKeyboardButton("الاشتراك في القناة 🚀", url=f"https://t.me/{VIP_CHANNEL_ID.replace('@','')}")]]
        await update.message.reply_text("⚠️ **عذراً، البوت للمشتركين فقط!**", reply_markup=InlineKeyboardMarkup(join_button), parse_mode='Markdown')

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    asset = query.data.replace("asset_", "")
    action = random.choice(["CALL 🟢", "PUT 🔴"])
    entry_time = (datetime.now() + timedelta(minutes=1)).strftime("%H:%M")
    
    signal_msg = f"🚀 **BOSS VIP SIGNAL**\n📦 الزوج: `{asset}`\n⏰ الدخول: `{entry_time}`\n💡 الإشارة: **{action}**"
    await query.edit_message_text(text=signal_msg, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("إشارة أخرى 🔄", callback_data=f"asset_{asset}")]]), parse_mode='Markdown')

if __name__ == '__main__':
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler('start', start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.run_polling()
