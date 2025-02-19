import json
from channels.generic.websocket import AsyncWebsocketConsumer
from django.utils import timezone
from channels.db import database_sync_to_async
from .models import Room, Message

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.room_group_name = f'chat_{self.room_id}'
        
        # Join group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        message_text = data.get('message', '')
        user = self.scope["user"]

        if not message_text or user.is_anonymous:
            return

        # Save message to DB
        room = await self._get_room(self.room_id)
        if not room:
            return

        new_msg = await database_sync_to_async(Message.objects.create)(
            room=room,
            sender=user,
            content=message_text,
            created_at=timezone.now()
        )

        # Broadcast to group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'sender': user.username,
                'message': message_text,
                'timestamp': new_msg.created_at.isoformat(),
            }
        )

    async def chat_message(self, event):
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'sender': event['sender'],
            'message': event['message'],
            'timestamp': event['timestamp'],
        }))

    @database_sync_to_async
    def _get_room(self, room_id):
        try:
            return Room.objects.get(pk=room_id)
        except Room.DoesNotExist:
            return None
