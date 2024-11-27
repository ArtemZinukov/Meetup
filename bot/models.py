from django.db import models


class BotUser(models.Model):
    ROLE_CHOICES = [
        ('listener', 'Слушатель'),
        ('speaker', 'Спикер'),
    ]

    telegram_id = models.BigIntegerField(unique=True, verbose_name="Telegram ID")
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='listener', verbose_name="Роль")

    def __str__(self):
        return f"{self.telegram_id} - {self.get_role_display()}"

    class Meta:
        app_label = 'bot'
        verbose_name = "Пользователь бота"
        verbose_name_plural = "Пользователи бота"

class Event:
    def __init__(self):
        self.speakers = []
        self.schedule = []
        self.donations = []

users = {}
events = Event()