from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.db import close_old_connections
import json
from .models import User, SubChannel, Message, Account


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        close_old_connections()
        self.unique_key = self.scope["url_route"]["kwargs"].get("unique_key")
        self.subchannel = await self.get_subchannel(self.unique_key)
        self.room_group_name = f'chat_{self.unique_key}'

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        if hasattr(self, 'room_group_name'):
            await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message_content = text_data_json.get("message")
        username = text_data_json.get("username")

        if message_content and username:
            user = await self.get_user(username)
            subchannel = await self.get_subchannel(self.unique_key)
            message = await self.create_message(user, subchannel, message_content)

            await self.send_one_to_group_message(message_content, username)

    async def send_one_to_group_message(self, message, username):
        user = await self.get_user(username)
        account = await self.get_account(user)

        # Debugging: Ensure profile picture URL is correct
        profile_picture_url = account.profile_picture.url if account.profile_picture else 'default_url_to_placeholder_image'
        print(f"Profile Picture URL: {profile_picture_url}")  # Debug print

        await self.channel_layer.group_send(
            self.room_group_name, {
                "type": "chat_message",
                "message": message,
                "username": username,
                "profile_picture_url": profile_picture_url,
            }
        )

    async def chat_message(self, event):
        message = event["message"]
        username = event["username"]
        profile_picture_url = event["profile_picture_url"]

        await self.send(text_data=json.dumps({
            "message": message,
            "username": username,
            "profile_picture_url": profile_picture_url,
        }))

    @sync_to_async
    def get_user(self, username):
        return User.objects.get(username=username)

    @sync_to_async
    def get_subchannel(self, unique_key):
        return SubChannel.objects.filter(unique_key=unique_key).first()

    @database_sync_to_async
    def create_message(self, user, subchannel, content):
        return Message.objects.create(content=content, sender=user, subchannel=subchannel)

    @database_sync_to_async
    def get_account(self, user):
        return Account.objects.get(user=user)
