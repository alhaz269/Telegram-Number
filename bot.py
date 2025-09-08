import os
import random
import csv
from io import StringIO
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

# ইউজার ডাটা স্টোরেজ
user_numbers = {}
user_gmails = {}

# /start কমান্ড
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = (
        "🌸 আসসালামু আলাইকুম 🌸\n"
        "👋 স্বাগতম! আপনি ১০০ নাম্বার বা 📬 Gmail দিতে পারেন ?\n\n"
        "📱 নাম্বার দিলে ➕ বা 🔗 বাটন আসবে\n"
        "📬 Gmail দিলে 📧 বাটন আসবে\n\n"
        "✅ একসাথে ১০০ টি নাম্বার দিন 😎"
    )
    await update.message.reply_text(welcome_text)

# /count কমান্ড
async def count_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    num_count = len(user_numbers.get(user_id, []))
    gmail_count = 1 if user_gmails.get(user_id) else 0
    await update.message.reply_text(
        f"আপনি {num_count} নাম্বার ইনপুট দিয়েছেন এবং {gmail_count} Gmail ইনপুট দিয়েছেন।"
    )

# ইউজারের ইনপুট হ্যান্ডলার
async def input_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text.strip()

    if "@" in text:  # Gmail ইনপুট
        user_gmails[user_id] = text
    else:  # নাম্বার ইনপুট
        numbers = [int(num) for num in text.replace(',', ' ').split() if num.isdigit()]
        if not numbers:
            await update.message.reply_text("সঠিক নাম্বার দিন।")
            return
        user_numbers[user_id] = numbers

    num_count = len(user_numbers.get(user_id, []))
    gmail_count = 1 if user_gmails.get(user_id) else 0
    await update.message.reply_text(
        f"আপনি {num_count} নাম্বার ইনপুট দিয়েছেন এবং {gmail_count} Gmail ইনপুট দিয়েছেন।"
    )

    keyboard = [
        [InlineKeyboardButton("➕ Add Plus", callback_data="plus_all")],
        [InlineKeyboardButton("🔗 Telegram Link", callback_data="link_all")],
        [InlineKeyboardButton("📧 Gmail Variations", callback_data="gmail")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("নিচের অপশনগুলো থেকে সিলেক্ট করুন:", reply_markup=reply_markup)

# বাটন হ্যান্ডলার
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    if query.data == "plus_all":
        numbers = user_numbers.get(user_id, [])
        if not numbers:
            await query.edit_message_text("কোনো নাম্বার পাওয়া যায়নি।")
            return
        sorted_numbers = sorted(numbers)
        result = "\n".join([f"+{num}" for num in sorted_numbers])
        await query.edit_message_text("➕ নাম্বারসমূহ:\n" + result)

    elif query.data == "link_all":
        numbers = user_numbers.get(user_id, [])
        if not numbers:
            await query.edit_message_text("কোনো নাম্বার পাওয়া যায়নি।")
            return
        result = "\n".join([f"https://t.me/+{num}" for num in numbers])
        await query.edit_message_text("নাম্বারগুলোর Telegram Link:\n" + result)

    elif query.data == "gmail":
        gmail = user_gmails.get(user_id)
        if not gmail:
            await query.edit_message_text("কোনো Gmail পাওয়া যায়নি।")
            return

        local_part, domain = gmail.split("@")
        letters = [c for c in local_part]

        variations = set()
        while len(variations) < 100:
            new_email = "".join([c.upper() if random.choice([True, False]) else c.lower() for c in letters])
            variations.add(new_email + "@" + domain)

        variations_list = list(variations)
        result_text = "\n".join(variations_list)
        await query.edit_message_text("📧 Gmail ভ্যারিয়েশনসমূহ:\n" + result_text)

        # CSV ফাইল তৈরি
        output = StringIO()
        writer = csv.writer(output)
        writer.writerow(["Gmail Variations"])
        for email in variations_list:
            writer.writerow([email])
        output.seek(0)
        await context.bot.send_document(chat_id=user_id, document=output, filename="gmail_variations.csv")

# ✅ বট টোকেন Environment Variable থেকে নেবে
BOT_TOKEN = os.getenv("BOT_TOKEN")

# অ্যাপ্লিকেশন সেটআপ
app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("count", count_command))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, input_handler))
app.add_handler(CallbackQueryHandler(button))

# বট রান
app.run_polling()
