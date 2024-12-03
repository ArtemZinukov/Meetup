# keyboards.py

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

def listener_keyboard():
    keyboard = [
        [InlineKeyboardButton('⁇ Задать вопрос', callback_data='handle_ask_question')],
        [InlineKeyboardButton('📺 Посмотреть программу', callback_data='view_program')],
        [InlineKeyboardButton('👥 Знакомства', callback_data='networking')],
        [InlineKeyboardButton('💵 Поддержать мероприятие', callback_data='donate')],
    ]
    return InlineKeyboardMarkup(keyboard)

def speaker_keyboard():
    keyboard = [
        [InlineKeyboardButton('🤷🏼‍♂️ Ответить на вопросы', callback_data='answer_questions')],
        [InlineKeyboardButton('📺 Посмотреть программу', callback_data='view_program')],
        [InlineKeyboardButton('⁇ Задать вопрос', callback_data='handle_ask_question')],
        [InlineKeyboardButton('👥Знакомства', callback_data='networking')],
        [InlineKeyboardButton('💵 Поддержать мероприятие', callback_data='donate')],
    ]
    return InlineKeyboardMarkup(keyboard)