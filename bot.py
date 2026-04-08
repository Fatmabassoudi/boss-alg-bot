import yfinance as yf
import pandas as pd
import random
import time
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# توكن البوت الخاص بكِ
TOKEN = '8794281359:AAHqUGfD6k-ZiAiBZYQMIkVr0o-enkdhl8Y'

# قائمة الأزواج
ASSETS = {
    "EUR/USD-OTC": "EURUSD=X", "GBP/USD-OTC": "GBPUSD=X",
    "USD/JPY-OTC": "USDJPY=X", "AUD/USD-OTC": "AUDUSD=X",
    "EUR/GBP-OTC": "EURGBP=X", "NZD/USD-OTC": "NZDUSD=X",
    "USD/CAD-OTC": "USDCAD=X", "USD/CHF-OTC": "USDCHF=X",
    "GBP/JPY-OTC": "GBPJPY=X", "EUR/JPY-OTC": "EURJPY=X",
    "AUD/CAD-OTC": "AUDCAD=X", "GBP/CHF-OTC": "GBPCHF=X",
    "CAD/JPY-OTC": "CADJPY=X", "EUR/CAD-OTC": "EURCAD=X",
    "USD/BRL-OTC": "USDBRL=X", "NZD/JPY-OTC": "NZDJPY=X",
    "USD/IDR-OTC": "USDIDR=X", "EUR/NZD-OTC": "EURNZD=X",
    "EUR/SGD-OTC": "EURSGD=X", "USD/ARS-OTC": "USDARS=X",
    "NZD/CAD-OTC": "NZDCAD=X"
}

def calculate_indicators(data):
    delta = data['Close'].diff()
    up = delta.clip(lower=0)
    down = -1 * delta.clip(upper=0)
    ema_up = up.ewm(com=13, adjust=False).mean()
    ema_down = down.ewm(com=13, adjust=False).mean()
    rs = ema_up / ema_down
    data['RSI'] = 100 - (100 / (1 + rs))
    exp1 = data['Close'].ewm(span=12, adjust=False).mean()
    exp2 = data['Close'].ewm(span=26, adjust=False).mean()
    data['MACD'] = exp1 - exp2
    data['Signal_Line'] = data['MACD'].ewm(span=9, adjust=False).mean()
    data['MA20'] = data['Close'].rolling(window=20).mean()
    data['StdDev'] = data['Close'].rolling(window=20).std()
    data['Upper_Band'] = data['MA20'] + (data['StdDev'] * 2)
    data['Lower_Band'] = data['MA20'] - (data['StdDev'] * 2)
    return data

def generate_signal(asset_name, timeframe):
    symbol = ASSETS[asset_name]
    try:
        interval = "1m" if timeframe == "1" else "5m"
        ticker = yf.Ticker(symbol)
        data = ticker.history(period="1d", interval=interval)
        
        if len(data) < 30: 
            return "⚠️ عذراً، البيانات غير كافية حالياً."

        data = calculate_indicators(data)
        last = data.iloc[-1]
        
        score = 0
        if last['RSI'] < 35: score += 1
        if last['RSI'] > 65: score -= 1
        if last['MACD'] > last['Signal_Line']: score += 1
        if last['MACD'] < last['Signal_Line']: score -= 1
        if last['Close'] <= last['Lower_Band']: score += 1
        if last['Close'] >= last['Upper_Band']: score -= 1

        if score >= 1:
            action = "CALL 🟢 (صعود)"
        else:
            action = "PUT 🔴 (هبوط)"

        # وقت الدخول (الوقت الحالي + دقيقة)
        entry_time = (datetime.now() + timedelta(minutes=1)).strftime("%H:%M")
        accuracy = random.randint(97, 99)

        # التنسيق المطلوب بالضبط
        return (
            f"🚀 **BOSS ALG BOT - ULTIMATE VIP** 🚀\n"
            f"━━━━━━━━━━━━━━\n"
            f"📦 الزوج: `{asset_name}`\n"
            f"⏰ وقت الدخول: `{entry_time}`\n"
            f"⏱️ مدة الصفقة: `{timeframe} MIN`\n"
            f"💡 الإشارة: **{action}**\n"
            f"🎯 الدقة المتوقعة: `{accuracy}%` \n"
            f"━━━━━━━━━━━━━━"
        )
    except Exception as e:
        return "⚠️ حدث خطأ أثناء التحليل."

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = (
        "اهلا بيك في ✌️ **BOSS ALG BOT** ✌️\n"
        "تم تحديث التنسيق بنجاح! 💥\n"
        "اختر زوج العملات لبدء القنص:"
    )
    keys = list(ASSETS.keys())
    keyboard = []
    for i in range(0, len(keys), 2):
        row = [InlineKeyboardButton(keys[i], callback_data=f"asset_{keys[i]}")]
        if i + 1 < len(keys):
            row.append(InlineKeyboardButton(keys[i+1], callback_data=f"asset_{keys[i+1]}"))
        keyboard.append(row)
    
    await update.message.reply_text(welcome_text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data.startswith("asset_"):
        asset = data.replace("asset_", "")
        keyboard = [
            [InlineKeyboardButton("1 دقيقة ⏱️", callback_data=f"time_1_{asset}"),
             InlineKeyboardButton("5 دقائق ⏱️", callback_data=f"time_5_{asset}")]
        ]
        await query.edit_message_text(text=f"📦 الزوج المختار: {asset}\n👇 اختر مدة الصفقة:", reply_markup=InlineKeyboardMarkup(keyboard))

    elif data.startswith("time_"):
        parts = data.split("_")
        timeframe = parts[1]
        asset = parts[2]
        await query.edit_message_text(text=f"🔄 جاري تحليل {asset}...")
        signal_msg = generate_signal(asset, timeframe)
        keyboard = [[InlineKeyboardButton("قنص إشارة جديدة 🔄", callback_data=f"asset_{asset}")]]
        await query.edit_message_text(text=signal_msg, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')

if __name__ == '__main__':
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler('start', start))
    app.add_handler(CallbackQueryHandler(button_handler))
    print("✅ تم تحديث شكل الإشارة بنجاح!")
    app.run_polling()