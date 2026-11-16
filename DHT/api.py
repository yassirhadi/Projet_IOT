import logging

from .models import Dht11
from .serializers import DHT11serialize
from rest_framework.decorators import api_view
from rest_framework import generics
from rest_framework.response import Response
from django.core.mail import send_mail
from django.conf import settings
import telebot

logger = logging.getLogger(__name__)

@api_view(['GET'])
def Dlist(request):
    all_data = Dht11.objects.all()
    data = DHT11serialize(all_data, many=True).data
    return Response({'data': data})

class Dhtviews(generics.CreateAPIView):
    queryset = Dht11.objects.all()
    serializer_class = DHT11serialize

    def perform_create(self, serializer):
        data = serializer.save()
        if data.temperature <= 25:
            return

        message = f"Alerte ! Temperature = {data.temperature} °C"
        if settings.EMAIL_HOST_USER and settings.EMAIL_HOST_PASSWORD and settings.ALERT_EMAIL_TO:
            try:
                send_mail(
                    subject="Alerte Temperature",
                    message=message,
                    from_email=settings.EMAIL_HOST_USER,
                    recipient_list=[settings.ALERT_EMAIL_TO],
                )
            except Exception as error:
                logger.warning("Email alert failed (%s)", type(error).__name__)

        if settings.TELEGRAM_TOKEN and settings.TELEGRAM_CHAT_ID:
            try:
                bot = telebot.TeleBot(settings.TELEGRAM_TOKEN)
                bot.send_message(settings.TELEGRAM_CHAT_ID, message, timeout=5)
            except Exception as error:
                logger.warning("Telegram alert failed (%s)", type(error).__name__)
