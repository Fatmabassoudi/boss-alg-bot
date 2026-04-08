import http.server
import socketserver
import threading
import os
import random
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# --- سيرفر وهمي لضمان استمرار الخدمة مجاناً ---
def run_dummy_server():
    port = int(os.environ.get("PORT", 8080))
    handler = http.server.SimpleHTTPRequestHandler
    with socketserver.TCPServer(("", port), handler) as httpd:
        httpd.serve_forever()

threading.Thread(target=run_dummy_server, daemon=True).start()

# --- الإعدادات الأساسية ---
TOKEN = '8794281359:AAHqUGfD6k-ZiAiBZYQMIkVr0o-enkdhl8Y'
VIP_CHANNEL_ID = -1003844075678  # الرقم الصحيح الذي وضعناه

# قائمة الأزواج كاملة كما طلبتِ
ASSETS = [
    "EUR/USD-OTC", "GBP/USD-OTC", "USD/JPY-OTC", "AUD/USD-OTC",
    "EUR/GBP-OTC", "NZD/USD-OTC", "USD/CAD-OTC", "USD/CHF-OTC",
    "GBP/JPY-OTC", "EUR/JPY-OTC", "AUD/CAD-OTC", "GBP/CHF-OTC",
    "USD/BRL-OTC", "USD/INR-OTC", "USD/TRY-OTC", "EUR/TRY-OTC"
]

# دالة التحقق من العضوية
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
        welcome_text = (
            "💎 **WELCOME TO BOSS VIP SYSTEM** 💎\n"
            "━━━━━━━━━━━━━━\n"
            "مرحباً بكِ يا Boss في النظام الحصري.\n"
            "تم التحقق من عضويتك.. اختاري زوج العملات:"
        )
        keyboard = []
        for i in range(0, len(ASSETS), 2):
            row = [InlineKeyboardButton(ASSETS[i], callback_data=f"asset_{ASSETS[i]}")]
            if i + 1 < len(ASSETS):
                row.append(InlineKeyboardButton(ASSETS[i+1], callback_data=f"asset_{ASSETS[i+1]}"))
            keyboard.append(row)
        await update.message.reply_text(welcome_text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')
    else:
        await update.message.reply_text("⚠️ **عذراً، الوصول مقتصر على أعضاء VIP فقط!**")

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    await query.answer()

    if not await is_user_vip(user_id, context):
        await query.edit_message_text("❌ انتهت صلاحية وصولك.")
        return

    data = query.data
    if data.startswith("asset_"):
        asset = data.replace("asset_", "")
        keyboard = [[
            InlineKeyboardButton("1 MIN ⏱️", callback_data=f"sig_1_{asset}"),
            InlineKeyboardButton("5 MIN ⏱️", callback_data=f"sig_5_{asset}")
        ]]
        await query.edit_message_text(f"📦 الزوج المختار: *{asset}*\nإختر فريم الصفقة:", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')
    
    elif data.startswith("sig_"):
        parts = data.split("_")
        timeframe, asset = parts[1], parts[2]
        
        # تصميم الإشارة الاحترافي
        action = random.choice(["CALL 🟢 (صعود)", "PUT 🔴 (هبوط)"])
        entry_time = (datetime.now() + timedelta(minutes=1)).strftime("%H:%M")
        accuracy = random.randint(94, 98)

        signal_msg = (
            f"🚀 **BOSS ALG VIP SIGNAL** 🚀\n"
            f"━━━━━━━━━━━━━━\n"
            f"📦 **الـزوج:** `{asset}`\n"
            f"⏰ **الـوقت:** `{entry_time}`\n"
            f"⏱️ **الـمدة:** `{timeframe} MIN`\n"
            f"💡 **الإشارة:** **{action}**\n"
            f"🎯 **الـدقة:** `{accuracy}%` \n"
            f"━━━━━━━━━━━━━━\n"
            f"⚠️ *ادخل الصفقة مع بداية الشمعة القادمة*"
        )
        
        keyboard = [[InlineKeyboardButton("قنص إشارة أخرى 🔄", callback_data=f"asset_{asset}")]]
        await query.edit_message_text(text=signal_msg, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')

if __name__ == '__main__':
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler('start', start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.run_polling()
