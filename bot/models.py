from django.db import models


class BotUser(models.Model):
    ROLE_CHOICES = [
        ('listener', 'Слушатель'),
        ('speaker', 'Спикер'),
    ]

    telegram_id = models.BigIntegerField(
        unique=True,
        verbose_name='Telegram ID')
    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES,
        default='listener',
        verbose_name='Роль')
    name = models.CharField(max_length=255, verbose_name='Имя', blank=True)
    consent_given = models.BooleanField(
        default=False,
        verbose_name='Согласие на обработку данных',
        null=True, blank=True)
    age = models.PositiveIntegerField(
        verbose_name='Возраст',
        null=True, blank=True)
    about_myself = models.TextField(verbose_name='О себе', blank=True)
    is_active_speaker = models.BooleanField(
            default=False,
            verbose_name='Статус активного спикера',)

    def __str__(self):
        return f"{self.telegram_id} - {self.get_role_display()} - {self.name}"

    class Meta:
        app_label = 'bot'
        verbose_name = 'Пользователь бота'
        verbose_name_plural = 'Пользователи бота'


class Event(models.Model):
    name = models.CharField(
        verbose_name='Название выступления',
        max_length=255)
    description = models.TextField(
        verbose_name='Описание выступления',
        blank=True)
    start_time = models.DateTimeField(
        verbose_name='Запланированное время - начало')
    end_time = models.DateTimeField(
        verbose_name='Запланированное время - конец')
    speaker = models.ForeignKey(
        BotUser,
        on_delete=models.CASCADE,
        related_name='speaking_events')

    def __str__(self):
        return f'{self.speaker} - {self.name}'

    class Meta:
        verbose_name = "Событие"
        verbose_name_plural = "События"


class Question(models.Model):
    STATUS_CHOICES = [
        ('new', 'Новый'),
        ('in_progress', 'В процессе'),
        ('answered', 'Отвеченный'),
    ]

    user = models.ForeignKey(BotUser, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    text = models.TextField(verbose_name='Вопрос')
    asked_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='new',
        verbose_name='Статус вопроса',
    )

    def __str__(self):
        return f'{self.user} - {self.event}'

    class Meta:
        verbose_name = 'Вопрос'
        verbose_name_plural = 'Вопросы'


class Donation(models.Model):
    user = models.ForeignKey(BotUser, on_delete=models.CASCADE)
    amount = models.PositiveIntegerField(verbose_name='Сумма доната')

    def __str__(self):
        return f'{self.user} - {self.amount}'

    class Meta:
        verbose_name = 'Донат'
        verbose_name_plural = 'Донаты'
