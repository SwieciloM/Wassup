import json
import base64
from channels.generic.websocket import AsyncWebsocketConsumer
from django.utils import timezone
from django.core.files.base import ContentFile
from channels.db import database_sync_to_async
from django.urls import reverse

from .models import Room, Message


class ChatConsumer(AsyncWebsocketConsumer):
    """Handles real-time chat via WebSocket."""

    async def connect(self):
        """Join the chat room group."""
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.room_group_name = f'chat_{self.room_id}'

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        """Leave the chat room group."""
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        """Handle incoming messages and broadcast them."""
        data = json.loads(text_data)
        message_text = data.get('message', '')
        image_data = data.get('image')
        user = self.scope["user"]

        if user.is_anonymous or (not message_text and not image_data):
            return

        room = await self._get_room(self.room_id)
        if not room:
            return

        image_file = None
        if image_data:
            try:
                header, encoded = image_data.split(';base64,')
                ext = header.split('/')[-1]
                file_name = f'chat_{self.room_id}_{timezone.now().timestamp()}.{ext}'
                image_file = ContentFile(base64.b64decode(encoded), name=file_name)
            except Exception as e:
                print("Error decoding image:", e)

        new_msg = await database_sync_to_async(Message.objects.create)(
            room=room,
            sender=user,
            content=message_text,
            image=image_file,
            created_at=timezone.now()
        )

        response = {
            'sender': user.username,
            'message': message_text,
            'timestamp': new_msg.created_at.isoformat(),
        }
        if new_msg.image:
            response['image_url'] = reverse('protected-media', kwargs={'message_id': new_msg.id})

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                **response,
            }
        )

    async def chat_message(self, event):
        """Send message to WebSocket."""
        await self.send(text_data=json.dumps({
            'sender': event['sender'],
            'message': event['message'],
            'timestamp': event['timestamp'],
            'image_url': event.get('image_url')
        }))

    @database_sync_to_async
    def _get_room(self, room_id):
        """Fetch room from DB."""
        try:
            return Room.objects.get(pk=room_id)
        except Room.DoesNotExist:
            return None
