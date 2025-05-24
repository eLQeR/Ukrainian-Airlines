"""Chat app URL Configuration"""

from django.urls import path
from .views import ChatView  # pylint: disable-all

urlpatterns = [
    path('chat/<str:chat_id>/', ChatView.as_view(), name='chat'),
]

app_name = 'chat_app'
