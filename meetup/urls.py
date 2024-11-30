from django.contrib import admin
from django.urls import path
from bot.views import yookassa_webhook

urlpatterns = [
    path('admin/', admin.site.urls),
    path('webhook/yookassa/', yookassa_webhook, name='yookassa_webhook'),
]
