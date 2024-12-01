from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext, MessageHandler, Filters
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup

from django.conf import settings
import os
import django
import uuid

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'meetup.settings')
django.setup()

from .models import BotUser, Donation, Schedule
from yookassa import Configuration, Payment

Configuration.configure(settings.YOOKASSA_SHOP_ID,
                        settings.YOOKASSA_SECRET_KEY)


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


def view_program(update: Update, context: CallbackContext) -> None:
    programs = Schedule.objects.all()

    if not programs:
        update.callback_query.message.reply_text("Программа еще не создана.")
        return

    program_text = "Программа мероприятия:\n\n"
    for program in programs:
        start_time = program.start_time.strftime("%H:%M")
        end_time = program.end_time.strftime("%H:%M")
        program_text += (f"{program.event.name}:{program.event.description}\nСпикер:{program.event.speaker.name}"
                         f"\nВремя: {start_time} - {end_time}\n\n")

    update.callback_query.message.reply_text(program_text)


def handle_callback(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()

    if query.data == "ask_question":
        query.edit_message_text("Напишите ваш вопрос. Укажите тему и содержание.")
    elif query.data == "view_program":
        view_program(update, context)
    elif query.data == "networking":
        query.edit_message_text("Сейчас загрузим анкеты для знакомств...")
    elif query.data == "donate":
        donate(update, context)
    elif query.data.startswith("donate_"):
        speaker_id = query.data.split("_")[1]
        context.user_data['speaker_id'] = speaker_id
        query.edit_message_text("Сколько вы хотите задонатить? Пожалуйста, укажите сумму в рублях.")
    elif query.data == "answer_questions":
        query.edit_message_text("Сейчас загрузим вопросы, поступившие от слушателей...")


def donate(update: Update, context: CallbackContext) -> None:
    speakers = BotUser.objects.filter(role='speaker')
    keyboard = []
    for speaker in speakers:
        keyboard.append(
            [InlineKeyboardButton(f"{speaker.name} - {speaker.username}", callback_data=f'donate_{speaker.telegram_id}')])

    reply_markup = InlineKeyboardMarkup(keyboard)
    update.callback_query.message.reply_text("Выберите спикера для доната:", reply_markup=reply_markup)


def handle_donation_amount(update: Update, context: CallbackContext) -> None:
    if 'speaker_id' not in context.user_data:
        update.message.reply_text("Сначала выберите спикера для доната.")
        return

    amount_text = update.message.text
    try:
        amount = float(amount_text)

        if amount <= 0:
            raise ValueError("Сумма должна быть положительной.")

        speaker_id = context.user_data['speaker_id']
        donor_id = update.effective_user.id

        donor = BotUser.objects.get(telegram_id=donor_id)
        speaker = BotUser.objects.get(telegram_id=speaker_id)

        Donation.objects.create(
            donor=donor,
            speaker=speaker,
            amount=amount,
        )

        payment = Payment.create({
            "amount": {
                "value": str(amount),
                "currency": "RUB"
            },
            "confirmation": {
                "type": "redirect",
                "return_url": "https://your-redirect-url.com"
            },
            "capture": True,
            "description": f"Донат спикеру ID {speaker_id}",
            "metadata": {
                "donor_id": donor_id,
                "speaker_id": speaker_id,
            }
        }, uuid.uuid4())

        update.message.reply_text(f"Перейдите по ссылке для оплаты: {payment.confirmation.confirmation_url}")

    except ValueError as e:
        update.message.reply_text(f"Ошибка: {e}. Пожалуйста, введите корректную сумму.")

    except Exception as e:
        update.message.reply_text(f"Произошла ошибка при создании платежа: временные проблемы на стороне Юкасса. Попробуйте еще раз!")


def main() -> None:
    token = settings.TELEGRAM_BOT_TOKEN

    updater = Updater(token)

    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))

    dispatcher.add_handler(CallbackQueryHandler(handle_callback))

    dispatcher.add_handler(CommandHandler("donate", donate))

    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_donation_amount))

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()