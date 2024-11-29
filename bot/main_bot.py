from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from .models import BotUser

from django.conf import settings
import os
import django
from environs import Env

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'meetup.settings')
django.setup()


def start(update: Update, context: CallbackContext) -> None:
    telegram_id = update.effective_user.id
    username = update.effective_user.username

    user, created = BotUser.objects.get_or_create(
        telegram_id=telegram_id,
        defaults={'role': 'listener'}
    )

    if created:
        update.message.reply_text(
            "Приветствуем вас на мероприятии Meetup! "
            "Вы зарегистрированы как слушатель. Вы можете задать вопросы спикерам, участвовать в нетворкинге, "
            "а также поддержать мероприятие с помощью донатов."
        )
    else:
        if user.role == 'listener':
            send_listener_welcome(update, context, user)
        elif user.role == 'speaker':
            send_speaker_welcome(update, context, user)


def send_listener_welcome(update: Update, context: CallbackContext, user: BotUser):
    keyboard = [
        [InlineKeyboardButton("Задать вопрос", callback_data="ask_question")],
        [InlineKeyboardButton("Посмотреть программу", callback_data="view_program")],
        [InlineKeyboardButton("Знакомства", callback_data="networking")],
        [InlineKeyboardButton("Поддержать мероприятие", callback_data="donate")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    update.message.reply_text(
        f"Добро пожаловать, {user.name}! "
        "Вы можете задавать вопросы спикерам, участвовать в знакомствах и следить за программой мероприятия.\n\n"
        "Выберите, что вы хотите сделать:",
        reply_markup=reply_markup
    )


def send_speaker_welcome(update: Update, context: CallbackContext, user: BotUser):
    # Кнопки для спикера
    keyboard = [
        [InlineKeyboardButton("Ответить на вопросы", callback_data="answer_questions")],
        [InlineKeyboardButton("Посмотреть программу", callback_data="view_program")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    update.message.reply_text(
        f"Добро пожаловать, {user.name}! "
        "Вы зарегистрированы как спикер.\n\n"
        "Вам доступны следующие действия:",
        reply_markup=reply_markup
    )


def handle_callback(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()

    if query.data == "ask_question":
        query.edit_message_text("Напишите ваш вопрос. Укажите тему и содержание.")
    elif query.data == "view_program":
        query.edit_message_text("Программа мероприятия:\n1. Открытие\n2. Первый доклад\n...")
    elif query.data == "networking":
        query.edit_message_text("Сейчас загрузим анкеты для знакомств...")
    elif query.data == "donate":
        query.edit_message_text("Вы можете поддержать мероприятие. Переведите сумму на счет...")
    elif query.data == "answer_questions":
        query.edit_message_text("Сейчас загрузим вопросы, поступившие от слушателей...")


# def get_schedule(update: Update, context: CallbackContext) -> None:
#     events = Event.objects.all()
    # schedule_text = "Программа мероприятия:\n" + "\n".join(events.schedule)
    # update.message.reply_text(schedule_text)


# def ask_question(update: Update, context: CallbackContext) -> None:
#     user_id = update.message.from_user.id
#     if BotUser.objects.filter(telegram_id=user_id).exists():
#         question = ' '.join(context.args)
#         if question:
#             events.speakers[-1].questions.append((user_id, question))
#             update.message.reply_text("Ваш вопрос отправлен докладчику.")
#         else:
#             update.message.reply_text("Пожалуйста, укажите вопрос после команды.")
#     else:
#         update.message.reply_text("Сначала зарегистрируйтесь с помощью /register.")


# def donate(update: Update, context: CallbackContext) -> None:
#     user_id = update.message.from_user.id
#     if BotUser.objects.filter(telegram_id=user_id).exists():
#         amount = context.args[0] if context.args else "не указана"
#         events.donations.append((user_id, amount))
#         update.message.reply_text(f"Спасибо за поддержку! Вы пожертвовали {amount}.")


def main() -> None:
    env = Env()
    env.read_env()
    token = env.str("TG_BOT_TOKEN")

    updater = Updater(token)

    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))

    dispatcher.add_handler(CallbackQueryHandler(handle_callback))

    # dispatcher.add_handler(CommandHandler("register", register_user))
    #
    # dispatcher.add_handler(CommandHandler("schedule", get_schedule))
    #
    # dispatcher.add_handler(CommandHandler("ask", ask_question))
    #
    # dispatcher.add_handler(CommandHandler("donate", donate))

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()