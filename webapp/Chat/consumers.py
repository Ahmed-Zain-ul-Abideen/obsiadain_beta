import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import User
from webapp.models import ChatMessages


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.me = self.scope["user"]
        self.other_username = self.scope["url_route"]["kwargs"]["username"]

        # ✅ fetch DB user safely
        self.other_user = await self.get_user(self.other_username)

        self.room_name = f"{min(self.me.username, self.other_username)}_{max(self.me.username, self.other_username)}"
        self.room_group_name = f"chat_{self.room_name}"

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data["message"]

        # ✅ save to DB safely
        await self.save_message(message)

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat_message",
                "message": message,
                "sender": self.me.username
            }
        )

    async def chat_message(self, event):
        await self.send(json.dumps({
            "message": event["message"],
            "sender": event["sender"]
        }))

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    @database_sync_to_async
    def get_user(self, username):
        return User.objects.get(username=username)

    @database_sync_to_async
    def save_message(self, message):
        return ChatMessages.objects.create(
            sender=self.me,
            receiver=self.other_user,
            message=message
        )
