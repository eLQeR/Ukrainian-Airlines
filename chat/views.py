"""Chat app views."""

import os
import uuid
import openai

from django.shortcuts import render
from django.http import JsonResponse
from drf_spectacular.utils import extend_schema
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from airlines_api.models import Flight
from airlines_api.serializers import FlightListSerializer
from .models import Chat, Message, ChatTemplate, SystemPrompt, User  # pylint: disable-all

GPT_MODEL = os.environ.get('GPT_MODEL', 'gpt-4o-mini')
APP_TAGS = ['Chat']

SYSTEM_PROMPT = """You are a helpful assistant.
You are a chatbot that can answer questions Ukrainian Airlines.

Here you can see available flights:
{flights}
"""




class ChatView(APIView):
    """
    User get created chat via created by client URL,
    and create own chat with own message memory.
    """

    @extend_schema(tags=APP_TAGS)
    def get(self, request, chat_id):
        # Check if template chat exists

        serializer = FlightListSerializer(Flight.objects.all(), many=True)
        serialized_flights = serializer.data
        system_prompt = SYSTEM_PROMPT.format(flights=serialized_flights)

        prompt = SystemPrompt.objects.get_or_create(user=User.objects.first(), prompt=system_prompt)[0]

        template_chat = ChatTemplate.objects.get_or_create(
            chat_id=chat_id, system_prompt=prompt.prompt, user=User.objects.first()
        )[0]

        # Create a chat with memory for every user that visit URL
        # user_chat_id = str(uuid.uuid4())
        user_chat = Chat.objects.get_or_create(
            user=None,
            system_prompt=template_chat.system_prompt,
            chat_id=chat_id
        )[0]

        messages = user_chat.messages.all().order_by('timestamp')
        return render(
            request,
            'chat/chat.html',
            {'chat_id': user_chat.chat_id, 'messages': messages}
        )

    @extend_schema(tags=APP_TAGS)
    def post(self, request, chat_id):
        # Check if chat for user exists
        try:
            chat = Chat.objects.get(chat_id=chat_id)
        except Chat.DoesNotExist:
            return Response({'error': 'Chat not found'}, status=status.HTTP_404_NOT_FOUND)

        user_message = request.POST.get('message')
        if not user_message:
            return Response({'error': 'Message is required'}, status=status.HTTP_400_BAD_REQUEST)

        # Save user message for the chat in DB
        Message.objects.create(chat=chat, sender='user', content=user_message)

        # Prepare message history
        messages = chat.messages.all().order_by('timestamp')
        message_history = [{'role': 'system', 'content': chat.system_prompt}]
        for message in messages:
            role = 'user' if message.sender == 'user' else 'assistant'
            message_history.append({'role': role, 'content': message.content})

        # Call to LLM
        response = openai.OpenAI().chat.completions.create(
            model=GPT_MODEL,
            messages=message_history
        )

        bot_reply = response.choices[0].message.content

        # Save LMM response to DB
        Message.objects.create(chat=chat, sender='bot', content=bot_reply)

        return JsonResponse({'reply': bot_reply})
