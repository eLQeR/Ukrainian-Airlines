"""Chat app models."""

from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class SystemPrompt(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='system_prompt')
    prompt = models.TextField()

    def __str__(self):
        return f'Prompt for {self.user.username}'


class ChatTemplate(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chat_templates')
    system_prompt = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    chat_id = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return f'Chat template {self.chat_id} by {self.user.username if self.user else "None"}'


class Chat(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chats', null=True)
    system_prompt = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    chat_id = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return f'Chat {self.chat_id} by {self.user.username if self.user else "None"}'


class Message(models.Model):
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name='messages')
    sender = models.CharField(max_length=10, choices=[('user', 'User'), ('bot', 'Bot')])
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.sender.capitalize()} message in chat {self.chat.chat_id}'
