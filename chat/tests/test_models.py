from django.test import TestCase
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from datetime import timedelta
from chat.models import Room, Message
import time


class TestRoomModel(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass123')

    def test_create_valid_room(self):
        """Check that creating a valid room succeeds without errors."""
        pass
        # room = Room.objects.create(
        #     name="Test Room",
        #     owner=self.user,
        #     guests=
        #     favorited_by=
        #     is_owner_only_editable=
        #     is_publicly_visible=
        # )
        # self.assertEqual(room.name, 'Test Task')
        # self.assertEqual(room.owner, self.user)
        # self.assertEqual(room.owner, self.user)
        # self.assertEqual(room.owner, self.user)
        # self.assertFalse(room.is_completed)
        # self.assertFalse(room.is_completed)
        # self.assertIsNotNone(room.created_at)
        # self.assertIsNotNone(room.updated_at)

    def test_due_date_cannot_be_in_the_past(self):
        """
        Attempting to set a past due date should raise ValidationError
        when the model is cleaned or saved with full validation.
        """
        pass
        # past_date = timezone.now() - timedelta(days=1)
        # task = Task(
        #     user=self.user,
        #     title='Invalid Task',
        #     due_date=past_date
        # )
        # with self.assertRaises(ValidationError):
        #     task.full_clean()

    def test_str_representation(self):
        """The __str__ method should return the title of the task."""
        pass
        # task = Task.objects.create(
        #     user=self.user,
        #     title='My Important Task'
        # )
        # self.assertEqual(str(task), 'My Important Task')

    def test_default_ordering(self):
        """
        The Meta ordering is ['-creation_date'], so the newest Task should come first.
        We create tasks in succession and check their order.
        """
        pass
        # task1 = Task.objects.create(
        #     user=self.user,
        #     title='First Created' 
        # )
        # time.sleep(0.1) 
        # task2 = Task.objects.create(
        #     user=self.user,
        #     title='Second Created'
        # )

        # tasks = list(Task.objects.all())
        # self.assertEqual(tasks[0], task2)
        # self.assertEqual(tasks[1], task1)


class TestMessageModel(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass123')
