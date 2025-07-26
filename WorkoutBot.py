import os
from flask import Flask, request
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters
from telegram.ext.webhookhandler import WebhookHandler

from workouts import generate_workouts, build_day_keyboard, build_difficulty_keyboard, WORKOUTS

# Словник для зберігання обраного рівня складності
user_difficulty = {}

# Flask
app = Flask(__name__)
TOKEN = os.getenv("BOT_TOKEN")
application = Application.builder().token(TOKEN).build()
webhook_handler = WebhookHandler(application)

@app.route("/")
def index():
    return "Бот працює!"

@app.post("/webhook")
async def telegram_webhook():
    return await webhook_handler.handle(request)

# Команди
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        'Привіт! Я твій фітнес-бот. Обери рівень складності тренувань:',
        reply_markup=build_difficulty_keyboard()
    )

async def list_days(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in user_difficulty:
        await update.message.reply_text(
            "Будь ласка, спочатку оберіть рівень складності за допомогою /start.",
            reply_markup=build_difficulty_keyboard()
        )
    else:
        await update.message.reply_text(
            f"Обери день тренування для рівня **{user_difficulty[user_id]}**:",
            reply_markup=build_day_keyboard(1),
            parse_mode='Markdown'
        )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    user_id = query.from_user.id

    if data.startswith("difficulty_"):
        difficulty_level = data.split("_")[1]
        user_difficulty[user_id] = difficulty_level
        await query.edit_message_text(f"Ти обрав рівень: **{difficulty_level}**.", parse_mode='Markdown')
        await query.message.reply_text(
            f"Обери день тренування зі списку для рівня **{difficulty_level}**:",
            reply_markup=build_day_keyboard(1), parse_mode='Markdown'
        )
    elif data.startswith("day_"):
        if user_id not in user_difficulty:
            await query.edit_message_text("Будь ласка, спочатку оберіть рівень складності за допомогою /start.")
            await query.message.reply_markup(reply_markup=build_difficulty_keyboard())
            return

        day_number = int(data.split("_")[1])
        selected_difficulty = user_difficulty[user_id]
        workout_data = WORKOUTS.get(day_number)

        if workout_data and selected_difficulty in workout_data:
            workout_list = workout_data[selected_difficulty]
            response = f"💪 **Тренування на День {day_number} ({selected_difficulty} рівень)**\n\n"
            
            response += "\n".join([f"• {item}" for item in workout_list])
        else:
            response = f"На жаль, тренування для дня {day_number} ({selected_difficulty} рівень) не знайдено."

        await query.edit_message_text(response, parse_mode='Markdown')
        keyboard_after_workout = [
            [InlineKeyboardButton("Обери інший день", callback_data="show_days_1")],
            [InlineKeyboardButton("Змінити рівень складності", callback_data="change_difficulty")]
        ]
        await query.message.reply_text("Що далі?", reply_markup=InlineKeyboardMarkup(keyboard_after_workout))
    elif data.startswith("page_"):
        page_number = int(data.split("_")[1])
        await query.edit_message_reply_markup(reply_markup=build_day_keyboard(page_number))
    elif data == "show_days_1":
        if user_id not in user_difficulty:
            await query.edit_message_text(
                "Будь ласка, спочатку оберіть рівень складності за допомогою /start.",
                reply_markup=build_difficulty_keyboard()
            )
        else:
            await query.edit_message_text(
                f"Обери день тренування зі списку для рівня **{user_difficulty[user_id]}**:",
                reply_markup=build_day_keyboard(1),
                parse_mode='Markdown'
            )
    elif data == "change_difficulty":
        await query.edit_message_text("Обери рівень складності тренувань:", reply_markup=build_difficulty_keyboard())

# Генеруємо тренування і додаємо обробники
generate_workouts()
application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("list", list_days))
application.add_handler(CallbackQueryHandler(button_handler))
