from django.contrib import admin
from .models import BotUser

@admin.register(BotUser)
class BotUserAdmin(admin.ModelAdmin):
    list_display = ('telegram_id', 'role')
    search_fields = ('telegram_id',)
