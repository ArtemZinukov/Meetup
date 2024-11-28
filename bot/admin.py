from django.contrib import admin
from .models import BotUser, Event, Question, Schedule, Donation

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

@admin.register(Donation)
class DonationAdmin(admin.ModelAdmin):
    list_display = ('user', 'amount')
    search_fields = ('user__username',)
    list_filter = ('user',)
