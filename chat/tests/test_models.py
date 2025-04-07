from django.test import TestCase
from django.contrib.auth.models import User
from chat.models import Room, Message
from django.core.files.uploadedfile import SimpleUploadedFile
from io import BytesIO
import time


class TestRoomModel(TestCase):
    def setUp(self):
        """Set up two users for testing room functionality."""
        self.user1 = User.objects.create_user(username="TestUser1", password="password123")
        self.user2 = User.objects.create_user(username="TestUser2", password="password123")

    def test_valid_room_creation(self):
        """Test whether a valid room can be created and all fields are set correctly."""
        room = Room.objects.create(
            name="Test Room",
            owner=self.user1,
            is_owner_only_editable=True,
            is_publicly_visible=False,
        )
        room.guests.add(self.user2)

        self.assertEqual(room.name, "Test Room")
        self.assertEqual(room.owner, self.user1)
        self.assertTrue(room.is_owner_only_editable)
        self.assertFalse(room.is_publicly_visible)
        self.assertEqual(room.guests.count(), 1)
        self.assertEqual(room.guests.first(), self.user2)
        self.assertIsNotNone(room.created_at)
        self.assertIsNotNone(room.updated_at)

    def test_str_representation(self):
        """Test whether the room's __str__ method returns the expected format."""
        room = Room.objects.create(
            name="Test Room",
            owner=self.user1,
            is_owner_only_editable=True,
            is_publicly_visible=False,
        )
        room.guests.add(self.user2)

        expected_str = f"Test Room (owner: {self.user1.username})"
        self.assertEqual(str(room), expected_str)

    def test_default_ordering(self):
        """Test whether rooms are ordered by creation date (newest first)."""
        room1 = Room.objects.create(
            name="Test Room",
            owner=self.user1,
            is_owner_only_editable=True,
            is_publicly_visible=False,
        )
        time.sleep(0.1)
        room2 = Room.objects.create(
            name="Second Test Room",
            owner=self.user2,
            is_owner_only_editable=True,
            is_publicly_visible=False,
        )

        rooms = Room.objects.all()
        self.assertEqual(rooms[0], room2)
        self.assertEqual(rooms[1], room1)

    def test_favorited_by(self):
        """Test whether the 'favorited_by' ManyToMany field functions correctly."""
        room = Room.objects.create(
            name="Test Room",
            owner=self.user1,
            is_owner_only_editable=True,
            is_publicly_visible=False,
        )
        room.guests.add(self.user2)
        room.favorited_by.add(self.user2)

        self.assertEqual(room.favorited_by.count(), 1)
        self.assertEqual(room.favorited_by.first(), self.user2)

    def test_meta_verbose_name(self):
        """Test whether the Room model has the correct verbose names."""
        self.assertEqual(Room._meta.verbose_name, "Room")
        self.assertEqual(Room._meta.verbose_name_plural, "Rooms")


class TestMessageModel(TestCase):
    def setUp(self):
        """Set up users and rooms for testing message functionality."""
        self.user1 = User.objects.create_user(username="TestUser1", password="password123")
        self.user2 = User.objects.create_user(username="TestUser2", password="password123")

        self.room = Room.objects.create(
            name="Test Room",
            owner=self.user1,
            is_owner_only_editable=True,
            is_publicly_visible=False,
        )

    def test_valid_message_creation(self):
        """Test whether a message with text content is created successfully."""
        message = Message.objects.create(
            room=self.room,
            sender=self.user1,
            content="Hello, world!",
        )
        self.assertEqual(message.room, self.room)
        self.assertEqual(message.sender, self.user1)
        self.assertEqual(message.content, "Hello, world!")
        self.assertIsNotNone(message.created_at)
        self.assertFalse(message.image)

    def test_valid_message_with_image(self):
        """Test whether a message with an image is created successfully."""
        image_data = BytesIO(b"fake_image_data")
        image_data.name = "test_image.jpg"
        image_file = SimpleUploadedFile(image_data.name, image_data.getvalue())

        message = Message.objects.create(
            room=self.room,
            sender=self.user1,
            image=image_file,
        )
        self.assertEqual(message.room, self.room)
        self.assertEqual(message.sender, self.user1)
        self.assertIsNone(message.content)
        self.assertTrue(message.image)

    def test_invalid_message_without_content_or_image(self):
        """Test whether creating a message fails when neither content nor image is provided."""
        with self.assertRaises(ValueError):
            Message.objects.create(
                room=self.room,
                sender=self.user1,
            )

    def test_str_representation_with_text(self):
        """Test whether the message's __str__ method with text content returns the expected format."""
        message = Message.objects.create(
            room=self.room,
            sender=self.user1,
            content="Hello, world!",
        )
        expected_str = f"User '{self.user1.username}' in room '{self.room.name}' at {message.created_at.strftime('%Y-%m-%d %H:%M:%S')}: Hello, world!"
        self.assertEqual(str(message), expected_str)

    def test_str_representation_with_image(self):
        """Test whether the message's __str__ method with image returns the expected format."""
        image_data = BytesIO(b"fake_image_data")
        image_data.name = "test_image.jpg"
        image_file = SimpleUploadedFile(image_data.name, image_data.getvalue())

        message = Message.objects.create(
            room=self.room,
            sender=self.user1,
            image=image_file,
        )
        expected_str = f"User '{self.user1.username}' in room '{self.room.name}' at {message.created_at.strftime('%Y-%m-%d %H:%M:%S')}: [image]"
        self.assertEqual(str(message), expected_str)

    def test_default_ordering(self):
        """Test whether messages are ordered by creation date (newest first)."""
        message1 = Message.objects.create(
            room=self.room,
            sender=self.user1,
            content="Message 1",
        )
        time.sleep(0.1)
        message2 = Message.objects.create(
            room=self.room,
            sender=self.user2,
            content="Message 2",
        )

        messages = Message.objects.all()
        self.assertEqual(messages[0], message2)
        self.assertEqual(messages[1], message1)

    def test_meta_verbose_name(self):
        """Test whether the Message model has the correct verbose names."""
        self.assertEqual(Message._meta.verbose_name, "Message")
        self.assertEqual(Message._meta.verbose_name_plural, "Messages")
