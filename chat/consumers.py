from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.sessions.backends.db import SessionStore
from django.conf import settings
from channels.db import database_sync_to_async
from django.db import close_old_connections
import json
from django.contrib.auth.models import User
from .models import *


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Close old database connections to prevent usage outside of async context
        close_old_connections()

        # Extract unique_key from the URL route
        self.unique_key = self.scope["url_route"]["kwargs"].get("unique_key")
        # Fetch the subchannel using the unique_key
        self.subchannel = await self.get_subchannel(self.unique_key)

        # Define room_group_name using the unique_key
        self.room_group_name = 'chat_%s' % self.unique_key

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        # Accept the WebSocket connection
        await self.accept()

    async def disconnect(self, close_code):
        if hasattr(self, 'room_group_name'):
            # Leave room group if room_group_name is initialized
            await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

        if hasattr(self, 'session_key'):
            # Clean up session key
            await self.delete_session_key()

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message_content = text_data_json.get("message")
        username = text_data_json.get("username")
        recipient = text_data_json.get("recipient")

        if message_content is not None and username is not None:
            user = await self.get_user(username)
            subchannel = await self.get_subchannel(self.unique_key)
            message = await self.create_message(user, subchannel, message_content)

            if recipient:
                await self.send_one_to_one_message(recipient, message_content, username)
            else:
                await self.send_one_to_group_message(message_content, username)

    async def send_one_to_group_message(self, message, username):
        await self.channel_layer.group_send(
            self.room_group_name, {
                "type": "chat.message",
                "message": message,
                "username": username,
            }
        )

    async def send_one_to_one_message(self, recipient, message, username):
        recipient_channel_name = await self.get_recipient_channel_name(recipient)
        if recipient_channel_name:
            await self.channel_layer.send(
                recipient_channel_name, {
                    "type": "chat.message",
                    "message": message,
                    "username": username,
                }
            )
        else:
            # Handle case where recipient is not found (offline, etc.)
            pass

    async def get_recipient_channel_name(self, recipient):
        # Logic to retrieve recipient's channel name (e.g., from a database)
        # This is a placeholder and should be replaced with your actual implementation
        return None  # Placeholder; replace with actual logic

    async def chat_message(self, event):
        message = event["message"]
        username = event["username"]
        await self.send(text_data=json.dumps(
            {"message": message,
             "username": username}
        ))

    @database_sync_to_async
    def get_user_id(self):
        if self.scope["user"].is_authenticated:
            return self.scope["user"].id
        else:
            return None

    @database_sync_to_async
    def get_user(self, username):
        return User.objects.get(username=username)

    @database_sync_to_async
    def get_subchannel(self, unique_key):
        return SubChannel.objects.filter(unique_key=unique_key).first()

    @database_sync_to_async
    def create_message(self, user, subchannel, content):
        return Message.objects.create(content=content, sender=user, subchannel=subchannel)
