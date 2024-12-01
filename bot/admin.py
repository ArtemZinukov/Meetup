from django.conf import settings
from django.contrib import admin
from .models import BotUser, Event, Question, Schedule, Donation
from telegram import Bot
import logging

@admin.register(BotUser)
class BotUserAdmin(admin.ModelAdmin):
    list_display = ('telegram_id', 'username', 'role', 'name', 'consent_given', 'age')
    search_fields = ('username', 'name')
    list_filter = ('role', 'consent_given')


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('name', 'speaker', 'start_time', 'end_time', 'is_active_event')
    search_fields = ('name', 'speaker__name')
    list_filter = ('is_active_event',)


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('user', 'event', 'text')
    search_fields = ('text',)
    list_filter = ('user', 'event')


@admin.register(Schedule)
class ScheduleAdmin(admin.ModelAdmin):
    list_display = ('start_time', 'end_time', 'user', 'event')
    search_fields = ('user__username', 'event__name')
    list_filter = ('user',)

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)

        if change:
            old_obj = Schedule.objects.get(id=obj.id)
            print(old_obj)
            if obj.event != old_obj.event or obj.end_time != old_obj.end_time:
                self.send_telegram_message_to_all_users()

    def send_telegram_message_to_all_users(self):
        bot_token = settings.TELEGRAM_BOT_TOKEN
        if not bot_token:
            return

        bot = Bot(token=bot_token)
        message = 'Произошли изменения в расписании!'

        users = BotUser.objects.all()

        for user in users:
            try:
                bot.send_message(chat_id=user.telegram_id, text=message)
                logging.info(f"Уведомление отправлено пользователю {user.telegram_id}")
            except Exception as e:
                logging.error(f"Ошибка при отправке уведомления пользователю {user.telegram_id}: {e}")


@admin.register(Donation)
class DonationAdmin(admin.ModelAdmin):
    list_display = ('donor', 'speaker', 'amount')
    search_fields = ('donor',)
    list_filter = ('donor',)
