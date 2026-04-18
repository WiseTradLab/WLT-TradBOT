import logging
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler,
    MessageHandler, filters, ContextTypes,
    ConversationHandler
)

# ===== CONFIG =====
TOKEN = "TON_NOUVEAU_TOKEN_ICI"

PIP_VALUES = {
    "EURUSD": 10,
    "XAUUSD": 1,
    "XAGUSD": 0.5,
    "BTCUSD": 1
}

# ===== STATES =====
CAPITAL, RISK, PIPS, ASSET, ENTRY = range(5)

# ===== CALCUL =====
def calculate_lot(capital, risk_percent, pips, pip_value):
    risk_dollar = capital * (risk_percent / 100)
    lot = risk_dollar / (pips * pip_value)
    return round(lot, 2)

# ===== START =====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [["📊 Calcul Lot", "🚀 Générer Signal"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    await update.message.reply_text(
        "🤖 WISE TRADING BOT\n\nChoisis une option 👇",
        reply_markup=reply_markup
    )

# ===== MENU =====
async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if text == "📊 Calcul Lot":
        await update.message.reply_text("💰 Entre ton capital ($):")
        return CAPITAL

    elif text == "🚀 Générer Signal":
        await update.message.reply_text("💰 Capital ($):")
        return CAPITAL

# ===== FLOW =====
async def get_capital(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["capital"] = float(update.message.text)
    await update.message.reply_text("⚠️ Risque (%) ?")
    return RISK

async def get_risk(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["risk"] = float(update.message.text)
    await update.message.reply_text("📉 Stop Loss (pips) ?")
    return PIPS

async def get_pips(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["pips"] = float(update.message.text)

    keyboard = [["EURUSD", "XAUUSD"], ["XAGUSD", "BTCUSD"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    await update.message.reply_text("📊 Choisis l’actif :", reply_markup=reply_markup)
    return ASSET

async def get_asset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    asset = update.message.text
    context.user_data["asset"] = asset

    await update.message.reply_text("📍 Prix d’entrée ?")
    return ENTRY

async def get_entry(update: Update, context: ContextTypes.DEFAULT_TYPE):
    entry = float(update.message.text)
    data = context.user_data

    capital = data["capital"]
    risk = data["risk"]
    pips = data["pips"]
    asset = data["asset"]

    pip_value = PIP_VALUES.get(asset, 1)

    lot = calculate_lot(capital, risk, pips, pip_value)

    # ===== SIGNAL FORMAT =====
    signal = (
        f"📊 SIGNAL TRADING\n\n"
        f"Actif: {asset}\n"
        f"Entrée: {entry}\n"
        f"SL: {pips} pips\n\n"
        f"💰 Lot: {lot}\n"
        f"Risque: {risk}%\n\n"
        f"🔥 Wise Trading Lab"
    )

    await update.message.reply_text(signal)

    return ConversationHandler.END

# ===== CANCEL =====
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ Annulé")
    return ConversationHandler.END

# ===== MAIN =====
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[MessageHandler(filters.TEXT & ~filters.COMMAND, menu)],
        states={
            CAPITAL: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_capital)],
            RISK: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_risk)],
            PIPS: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_pips)],
            ASSET: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_asset)],
            ENTRY: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_entry)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(conv_handler)

    print("✅ Bot en cours d'exécution...")
    app.run_polling()

if __name__ == "__main__":
    main()
