from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext, MessageHandler, Filters
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ParseMode

from django.conf import settings
import os
import django
import uuid

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'meetup.settings')
django.setup()

from .models import BotUser, Donation, Event, Question
from .keyboards import listener_keyboard, speaker_keyboard
from yookassa import Configuration, Payment

Configuration.configure(settings.YOOKASSA_SHOP_ID,
                        settings.YOOKASSA_SECRET_KEY)


def start(update: Update, context: CallbackContext) -> None:
    telegram_id = update.effective_user.id
    username = update.effective_user.username

    user, created = BotUser.objects.get_or_create(
        telegram_id=telegram_id,
        defaults={'role': 'listener', 'username': username}
    )

    if created:
        update.message.reply_text(
            'Приветствуем вас на мероприятии *Meetup*! \n\n'
            'Вы зарегистрированы как слушатель. \n\n'
            'Вы можете задать вопросы спикерам, участвовать в нетворкинге, '
            'а также поддержать мероприятие с помощью *донатов*.',
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=get_main_menu(update)
        )
    else:
        if user.role == 'listener':
            update.message.reply_text(
                f'Добро пожаловать, *{user.username}*! \n\n'
                'Вы можете задавать вопросы спикерам, участвовать в знакомствах и следить за программой мероприятия.\n\n'
                'Выберите, что вы хотите сделать:',
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=get_main_menu(update)
            )
        elif user.role == 'speaker':
            update.message.reply_text(
                f'Добро пожаловать, *{user.username}*! \n\n'
                'Вы зарегистрированы как *спикер*.\n\n'
                'Вам доступны следующие действия:',
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=get_main_menu(update)
            )


def get_main_menu(update: Update):
    telegram_id = update.effective_user.id
    user = BotUser.objects.get(telegram_id=telegram_id)

    if user.role == 'listener':
        keyboard = listener_keyboard()
        return keyboard

    elif user.role == 'speaker':
        keyboard = speaker_keyboard()
        return keyboard


def handle_ask_question(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()

    active_event = Event.objects.filter(is_active_event=True).first()

    if not active_event:
        query.edit_message_text(
            'Выступление закончилось. Попробуйте задать вопрос позже.',
            reply_markup=get_main_menu(update)
        )
        return

    context.user_data['active_event_id'] = active_event.id

    query.edit_message_text(
        f'Сейчас выступает спикер *{active_event.speaker.username}* с докладом: *{active_event.name}*.\n\n'
        'Пожалуйста, напишите ваш вопрос в ответ на это сообщение.',
        parse_mode=ParseMode.MARKDOWN,
    )


def handle_question_message(update: Update, context: CallbackContext):
    active_event_id = context.user_data.get('active_event_id')

    if not active_event_id:
        update.message.reply_text(
            'Не удалось определить текущее выступление. Пожалуйста, нажмите \'Задать вопрос\' снова.',
            reply_markup=get_main_menu(update)
        )
        return

    try:
        active_event = Event.objects.get(id=active_event_id, is_active_event=True)
    except Event.DoesNotExist:
        update.message.reply_text(
            'К сожалению, выступление завершилось.',
            reply_markup=get_main_menu(update)
        )
        context.user_data.pop('active_event_id', None)
        return

    try:
        user = BotUser.objects.get(telegram_id=update.effective_user.id)
    except BotUser.DoesNotExist:
        update.message.reply_text(
            'Ошибка: ваш профиль не найден. Пожалуйста, используйте команду /start для регистрации.'
        )
        return

    question_text = update.message.text.strip()

    if not question_text:
        update.message.reply_text('Пожалуйста, напишите ваш вопрос.')
        return

    Question.objects.create(
        user=user,
        event=active_event,
        text=question_text
    )

    update.message.reply_text(
        f'Ваш вопрос передан спикеру *{active_event.speaker.username}* \n\n'
        'Спикер ответит на вопросы после завершения доклада.',
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=get_main_menu(update)
    )

    context.user_data.pop('active_event_id', None)


def view_program(update: Update, context: CallbackContext) -> None:
    programs = Event.objects.all().order_by('start_time')

    if not programs:
        update.callback_query.message.reply_text("Программа еще не создана.")
        return

    program_text = "Программа мероприятия:\n\n"
    for program in programs:
        start_time = program.start_time.strftime("%H:%M")
        program_text += (f"*{program.name}* : _{program.description}_\nСпикер : *{program.speaker.name}*"
                         f"\nВремя начала выступления : *{start_time}*\n\n")

    update.callback_query.message.reply_text(
        program_text,
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=get_main_menu(update)
    )


def handle_callback(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()

    if query.data == "networking":
        query.edit_message_text("Сейчас загрузим анкеты для знакомств...")
    elif query.data == "donate":
        donate(update, context)
    elif query.data.startswith("donate_"):
        speaker_id = query.data.split("_")[1]
        context.user_data['speaker_id'] = speaker_id
        query.edit_message_text("Сколько вы хотите задонатить? Пожалуйста, укажите сумму в рублях.")


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

    dispatcher.add_handler(CallbackQueryHandler(handle_ask_question, pattern="^handle_ask_question$"))

    dispatcher.add_handler(CallbackQueryHandler(view_program, pattern="^view_program$"))

    dispatcher.add_handler(CallbackQueryHandler(handle_callback, pattern="^handle_callback$"))

    dispatcher.add_handler(CommandHandler("donate", donate))

    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_question_message))

    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_donation_amount))

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()