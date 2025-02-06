from django.urls import path
from .views import handle_voice_call_action_webhook

urlpatterns = [
    path('voice-webhook/', handle_voice_call_action_webhook, name='voice_webhook'),
]
