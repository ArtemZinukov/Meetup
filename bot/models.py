from django.db import models


class BotUser(models.Model):
    ROLE_CHOICES = [
        ('listener', 'Слушатель'),
        ('speaker', 'Спикер'),
    ]

    telegram_id = models.BigIntegerField(unique=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)

    def __str__(self):
        return f"{self.telegram_id} - {self.get_role_display()}"

    class Meta:
        app_label = 'bot'

class Event:
    def __init__(self):
        self.speakers = []
        self.schedule = []
        self.donations = []

users = {}
events = Event()