from django.urls import path
from .views import integrate_recordings

urlpatterns = [
    path('integrate-recordings/', integrate_recordings, name='integrate_recordings'),
]
