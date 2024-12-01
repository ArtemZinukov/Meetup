from django.contrib import admin
from django.conf import settings
from telegram import Bot
import logging

from .models import BotUser, Event, Question, Donation
from .keyboards import listener_keyboard, speaker_keyboard

logger = logging.getLogger(__name__)


@admin.register(BotUser)
class BotUserAdmin(admin.ModelAdmin):
    list_display = ('telegram_id', 'username', 'role', 'name', 'consent_given', 'age')
    search_fields = ('username', 'name')
    list_filter = ('role', 'consent_given')


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('name', 'speaker', 'start_time', 'is_active_event')
    search_fields = ('name', 'speaker__username')
    list_filter = ('is_active_event', 'speaker')

    def save_model(self, request, obj, form, change):
        if change:
            old_obj = Event.objects.get(pk=obj.pk)
            old_values = {
                'name': old_obj.name,
                'description': old_obj.description,
                'start_time': old_obj.start_time,
            }
        else:
            old_values = {}

        super().save_model(request, obj, form, change)

        self.send_telegram_message_to_all_users(obj, old_values, change)

    def send_telegram_message_to_all_users(self, obj, old_values, change):
        bot_token = settings.TELEGRAM_BOT_TOKEN

        bot = Bot(token=bot_token)

        if not change:
            message = f'Новое событие "{obj.name}" было добавлено.'
        else:
            changed_fields = []
            if old_values.get('name') != obj.name:
                changed_fields.append(f'Название: "{old_values.get("name")}" → "{obj.name}"')
            if old_values.get('start_time') != obj.start_time:
                old_time = old_values.get('start_time').strftime('%H:%M')
                new_time = obj.start_time.strftime('%H:%M')
                changed_fields.append(f'Время начала: "{old_time}" → "{new_time}"')

            if not changed_fields:
                return

            message = f'Событие "{obj.name}" было обновлено.\n\nИзменения:\n' + '\n'.join(changed_fields)

        users = BotUser.objects.all()
        for user in users:
            try:
                if user.role == 'listener':
                    keyboard = listener_keyboard()
                else:
                    keyboard = speaker_keyboard()
                bot.send_message(chat_id=user.telegram_id, text=message,reply_markup=keyboard, parse_mode='Markdown')
                logger.info(f'Уведомление отправлено пользователю {user.telegram_id}')
            except Exception as e:
                logger.error(f'Ошибка при отправке уведомления пользователю {user.telegram_id}: {e}')


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('user', 'event', 'text')
    search_fields = ('text',)
    list_filter = ('user', 'event')


@admin.register(Donation)
class DonationAdmin(admin.ModelAdmin):
    list_display = ('donor', 'speaker', 'amount')
    search_fields = ('donor',)
    list_filter = ('donor',)
