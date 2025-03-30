from django.test import TestCase
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from datetime import timedelta
from chat.models import Room, Message
import time


class TestRoomModel(TestCase):
    def setUp(self):
        """Set up two users for testing room functionality."""
        self.user1 = User.objects.create_user(username="TestUser1", password="password123")
        self.user2 = User.objects.create_user(username="TestUser2", password="password123")

    def test_valid_room_creation(self):
        """Test creating a valid room and ensure all fields are set correctly."""
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
        """Test the string representation of the room."""
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
        """Test that rooms are ordered by creation date (newest first)."""
        room1 = Room.objects.create(
            name="Test Room",
            owner=self.user1,
            is_owner_only_editable=True,
            is_publicly_visible=False,
        )
        room2 = Room.objects.create(
            name="Second Test Room",
            owner=self.user2,
            is_owner_only_editable=True,
            is_publicly_visible=False,
        )

        rooms = Room.objects.all()
        self.assertEqual(rooms[0], room1)
        self.assertEqual(rooms[1], room2)

    def test_favorited_by(self):
        """Test the ManyToMany relationship for favorited_by field."""
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
        """Test the verbose name options for the model."""
        self.assertEqual(Room._meta.verbose_name, "Room")
        self.assertEqual(Room._meta.verbose_name_plural, "Rooms")


class TestMessageModel(TestCase):
    def setUp(self):
        pass
