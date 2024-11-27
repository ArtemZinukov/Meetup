from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext, MessageHandler, Filters
# from django.conf import settings
# import os
# import django
from environs import Env

# # Настройка Django
# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'meetup.settings')
# django.setup()

# from .models import BotUser, Event, Question, Donation


def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text("Привет! Я бот для мероприятия. Для регистрации пропишите /register."
                              "Чтобы узнать о функционале, напишите /help.")


def help_command(update: Update, context: CallbackContext) -> None:
    update.message.reply_text(
        "Я могу помочь вам:\n"
        "- Узнать о мероприятии\n"
        "- Задать вопрос докладчику\n"
        "- Получить программу мероприятия\n"
        "- Познакомиться с другими разработчиками\n"
        "- Поддержать организатора\n"
    )


# def register_user(update: Update, context: CallbackContext) -> None:
#     user_id = update.message.from_user.id
#
#
#     if not BotUser.objects.filter(telegram_id=user_id).exists():
#         user = BotUser(telegram_id=user_id, role='listener')
#         user.save()
#         update.message.reply_text("Вы зарегистрированы как слушатель.")
#     else:
#         update.message.reply_text("Вы уже зарегистрированы.")


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

    dispatcher.add_handler(CommandHandler("help", help_command))

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