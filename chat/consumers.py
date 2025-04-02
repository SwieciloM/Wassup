import json
import base64
from channels.generic.websocket import AsyncWebsocketConsumer
from django.utils import timezone
from django.core.files.base import ContentFile
from channels.db import database_sync_to_async
from django.urls import reverse

from .models import Room, Message

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.room_group_name = f'chat_{self.room_id}'

        # Join room group
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
        image_data = data.get('image', None)
        user = self.scope["user"]

        if (not message_text and not image_data) or user.is_anonymous:
            return

        # Get the room (wrapped in database_sync_to_async)
        room = await self._get_room(self.room_id)
        if not room:
            return

        image_file = None
        if image_data:
            try:
                # The image_data is expected to be a Data URL (e.g., "data:image/png;base64,iVBORw0KG...")
                header, encoded = image_data.split(';base64,')
                # Extract file extension from header, e.g., "data:image/png"
                ext = header.split('/')[-1]
                # Create a file name with a timestamp.
                file_name = f'chat_{self.room_id}_{timezone.now().timestamp()}.{ext}'
                image_file = ContentFile(base64.b64decode(encoded), name=file_name)
            except Exception as e:
                # If decoding fails, ignore the image.
                print("Error decoding image:", e)

        # Save message to DB (using database_sync_to_async)
        new_msg = await database_sync_to_async(Message.objects.create)(
            room=room,
            sender=user,
            content=message_text,
            image=image_file,  # This can be None if no image was sent.
            created_at=timezone.now()
        )

        # Prepare the response data.
        response = {
            'sender': user.username,
            'message': message_text,
            'timestamp': new_msg.created_at.isoformat(),
        }
        if new_msg.image:
            response['image_url'] = reverse('protected_media', kwargs={'message_id': new_msg.id})

        # Broadcast to the group.
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                **response,
            }
        )

    async def chat_message(self, event):
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'sender': event['sender'],
            'message': event['message'],
            'timestamp': event['timestamp'],
            'image_url': event.get('image_url')  # May be None if no image.
        }))

    @database_sync_to_async
    def _get_room(self, room_id):
        try:
            return Room.objects.get(pk=room_id)
        except Room.DoesNotExist:
            return None
