
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

TOKEN = "YOUR_BOT_TOKEN"
ADMIN_ID = 123456789

user_orders = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    button = KeyboardButton(
        text="📱 Ирсоли рақам",
        request_contact=True
    )

    keyboard = ReplyKeyboardMarkup(
        [[button]],
        resize_keyboard=True
    )

    await update.message.reply_text(
        "Салом! Барои регистрация рақаматонро фиристед.",
        reply_markup=keyboard
    )

async def contact_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = ReplyKeyboardMarkup(
        [
            ["📦 Бор фармоиш додан"],
            ["📋 Борҳои ман"]
        ],
        resize_keyboard=True
    )

    await update.message.reply_text(
        "✅ Регистрация анҷом шуд",
        reply_markup=keyboard
    )

async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if text == "📦 Бор фармоиш додан":
        context.user_data["waiting_photo"] = True

        await update.message.reply_text(
            "📷 Лутфан акси маҳсулотро фиристед"
        )

async def photo_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.user_data.get("waiting_photo"):
        return

    photo = update.message.photo[-1]
    file_id = photo.file_id

    user_id = update.message.from_user.id
    name = update.message.from_user.full_name

    caption = f'''
📦 Закази нав

👤 Клиент: {name}
🆔 User ID: {user_id}

⏳ Барои ҷавоб ба ҳамин хабар Reply кунед
'''

    sent = await context.bot.send_photo(
        chat_id=ADMIN_ID,
        photo=file_id,
        caption=caption
    )

    user_orders[sent.message_id] = user_id

    await update.message.reply_text(
        "✅ Дархости шумо қабул шуд\n\n⏳ Ҷавоби админро интизор шавед"
    )

    context.user_data["waiting_photo"] = False

async def admin_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.chat_id != ADMIN_ID:
        return

    if not update.message.reply_to_message:
        return

    reply_message_id = update.message.reply_to_message.message_id

    if reply_message_id not in user_orders:
        return

    client_id = user_orders[reply_message_id]

    await context.bot.send_message(
        chat_id=client_id,
        text=f"📩 Ҷавоби админ:\n\n{update.message.text}"
    )

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.CONTACT, contact_handler))
app.add_handler(MessageHandler(filters.PHOTO, photo_handler))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))
app.add_handler(MessageHandler(filters.TEXT & filters.REPLY, admin_reply))

print("Bot started...")
app.run_polling()
