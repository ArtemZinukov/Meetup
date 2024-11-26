from django.db import models


class BotUser(models.Model):
    telegram_id = models.BigIntegerField(unique=True)
    role = models.CharField(max_length=10)  # 'speaker' или 'listener'

    def __str__(self):
        return f"{self.telegram_id} - {self.role}"

    class Meta:
        app_label = 'bot'

class Event:
    def __init__(self):
        self.speakers = []
        self.schedule = []
        self.donations = []

users = {}
events = Event()