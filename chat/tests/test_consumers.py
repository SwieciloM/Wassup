import json
import base64
import tempfile
import os
import asyncio
from django.test import TransactionTestCase
from django.contrib.auth.models import User
from django.urls import path, reverse
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from channels.testing import WebsocketCommunicator

from chat.consumers import ChatConsumer
from chat.models import Room, Message


# Reusable ASGI application for WebSocket tests
application = ProtocolTypeRouter({
    "websocket": AuthMiddlewareStack(
        URLRouter([
            path("ws/chat/<int:room_id>/", ChatConsumer.as_asgi()),
        ])
    )
})


class TestChatConsumer(TransactionTestCase):
    def setUp(self):
        """Set up ASGI app, event loop, and default room owner for WebSocket tests."""
        self.application = application
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.owner = User.objects.create_user(username="owner", password="pass")

    def tearDown(self):
        """Close the event loop after tests."""
        self.loop.close()

    def run_async(self, coroutine):
        """Run an async coroutine in the test event loop."""
        return self.loop.run_until_complete(coroutine)

    def test_connect_and_disconnect(self):
        """Test that connecting to a valid room is accepted and disconnects cleanly."""
        room = Room.objects.create(owner=self.owner, name="Connect Room")

        async def inner():
            communicator = WebsocketCommunicator(
                self.application, f"/ws/chat/{room.id}/"
            )
            communicator.scope["user"] = self.owner
            connected, _ = await communicator.connect()
            self.assertTrue(connected)
            await communicator.disconnect()

        self.run_async(inner())

    def test_receive_text_message_creates_record_and_broadcast(self):
        """Test that sending a text message creates a Message in the DB and broadcasts it back."""
        temp_media = tempfile.mkdtemp()
        with self.settings(MEDIA_ROOT=temp_media):
            user = User.objects.create_user(username="textuser", password="pwd")
            room = Room.objects.create(owner=user, name="Text Room")

            from channels.db import database_sync_to_async

            async def inner():
                communicator = WebsocketCommunicator(
                    self.application, f"/ws/chat/{room.id}/"
                )
                communicator.scope["user"] = user
                connected, _ = await communicator.connect()
                self.assertTrue(connected)

                payload = {"message": "Hello Channels!"}
                await communicator.send_json_to(payload)

                response = await communicator.receive_json_from()
                self.assertEqual(response["sender"], user.username)
                self.assertEqual(response["message"], payload["message"])
                self.assertIn("timestamp", response)

                await communicator.disconnect()

                # Database assertions via database_sync_to_async
                msg = await database_sync_to_async(Message.objects.get)(room=room, sender=user)
                self.assertEqual(msg.content, payload["message"])
                self.assertFalse(msg.image)

            self.run_async(inner())

    def test_receive_image_message_creates_file_and_broadcast(self):
        """Test that sending a base64-encoded image saves a file and broadcasts an image URL."""
        temp_media = tempfile.mkdtemp()
        with self.settings(MEDIA_ROOT=temp_media):
            user = User.objects.create_user(username="imguser", password="pwdimg")
            room = Room.objects.create(owner=user, name="Image Room")

            raw = b"imagebytes"
            encoded = base64.b64encode(raw).decode()
            image_data = f"data:image/png;base64,{encoded}"

            from channels.db import database_sync_to_async

            async def inner():
                communicator = WebsocketCommunicator(
                    self.application, f"/ws/chat/{room.id}/"
                )
                communicator.scope["user"] = user
                connected, _ = await communicator.connect()
                self.assertTrue(connected)

                await communicator.send_json_to({"image": image_data})
                response = await communicator.receive_json_from()
                self.assertEqual(response["sender"], user.username)
                self.assertIn("image_url", response)

                await communicator.disconnect()

                # Database and file system assertions
                msg = await database_sync_to_async(Message.objects.get)(room=room, sender=user)
                self.assertTrue(msg.image.name)
                file_path = os.path.join(temp_media, msg.image.name)
                self.assertTrue(os.path.exists(file_path))

            self.run_async(inner())

    def test_receive_empty_payload_no_action(self):
        """Test that empty payload does not save or broadcast any messages."""
        user = User.objects.create_user(username="emptyuser", password="pw")
        room = Room.objects.create(owner=user, name="Empty Room")

        async def inner():
            communicator = WebsocketCommunicator(
                self.application, f"/ws/chat/{room.id}/"
            )
            communicator.scope["user"] = user
            connected, _ = await communicator.connect()
            self.assertTrue(connected)

            await communicator.send_json_to({"message": "", "image": None})
            with self.assertRaises(Exception):
                await communicator.receive_json_from(timeout=0.5)

            await communicator.disconnect()

        self.run_async(inner())
        self.assertFalse(Message.objects.filter(room=room).exists())

    def test_anonymous_user_cannot_send(self):
        """Test that anonymous users can connect but cannot send messages."""
        room = Room.objects.create(owner=self.owner, name="Anon Room")

        async def inner():
            communicator = WebsocketCommunicator(
                self.application, f"/ws/chat/{room.id}/"
            )
            connected, _ = await communicator.connect()
            self.assertTrue(connected)

            await communicator.send_json_to({"message": "Hi"})
            with self.assertRaises(Exception):
                await communicator.receive_json_from(timeout=0.5)

            await communicator.disconnect()

        self.run_async(inner())
        self.assertFalse(Message.objects.exists())
