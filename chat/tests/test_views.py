from django.test import TestCase, RequestFactory, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from pathlib import Path
from django.conf import settings
from chat.models import Room, Message

class TestRoomListView(TestCase):
    def setUp(self):
        """Set up users and rooms to test room categorization in RoomListView."""
        self.factory = RequestFactory()
        self.client = Client()
        self.user1 = User.objects.create_user(username="user1", password="testpass")
        self.user2 = User.objects.create_user(username="user2", password="testpass")
        # Create a room owned by user1.
        self.room_owned = Room.objects.create(owner=self.user1, name="Owned Room")
        # Create a room where user1 is a guest but not owner.
        self.room_joined = Room.objects.create(owner=self.user2, name="Joined Room", is_publicly_visible=False)
        self.room_joined.guests.add(self.user1)
        # Create a public room where user1 is neither owner nor guest.
        self.room_public = Room.objects.create(owner=self.user2, name="Public Room", is_publicly_visible=True)

    def test_room_categories_in_context(self):
        """Test that RoomListView context contains proper categorized room lists."""
        self.client.login(username="user1", password="testpass")
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('my_rooms', response.context)
        self.assertIn('joined_rooms', response.context)
        self.assertIn('public_rooms', response.context)

        my_rooms = response.context['my_rooms']
        joined_rooms = response.context['joined_rooms']
        public_rooms = response.context['public_rooms']
        self.assertIn(self.room_owned, my_rooms)
        self.assertIn(self.room_joined, joined_rooms)
        self.assertIn(self.room_public, public_rooms)


class TestRoomDetailView(TestCase):
    def setUp(self):
        """Set up a room with messages and users for testing RoomDetailView."""
        self.factory = RequestFactory()
        self.client = Client()
        self.user = User.objects.create_user(username="user1", password="testpass")
        self.other_user = User.objects.create_user(username="user2", password="testpass")
        self.room = Room.objects.create(owner=self.user, name="Test Room")
        self.room.guests.add(self.other_user)
        # Create 25 messages; only the 20 most recent should be in the context.
        for i in range(25):
            Message.objects.create(room=self.room, sender=self.user, content=f"Test Message {i}")
        # Refresh the room instance so that a later query sees the messages.
        self.room.refresh_from_db()

    def test_get_context_data(self):
        """Test that RoomDetailView context includes the room, exactly 20 messages and a message form."""
        self.client.login(username="user1", password="testpass")
        response = self.client.get(reverse('room', kwargs={'pk': self.room.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertIn('room', response.context)
        self.assertIn('messages', response.context)
        self.assertIn('message_form', response.context)
        # Convert the iterator to a list and verify its length.
        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 20,
                         f"Expected exactly 20 recent messages in context, got {len(messages)}.")

    def test_post_valid_message(self):
        """Test posting a valid new message via RoomDetailView."""
        self.client.login(username="user1", password="testpass")
        post_data = {'content': "Hello, this is a new message."}
        response = self.client.post(reverse('room', kwargs={'pk': self.room.pk}), data=post_data)
        self.assertEqual(response.status_code, 302,
                         "Expected a redirect after valid POST.")
        # There should now be 26 messages (25 from setUp plus the new one)
        self.assertEqual(Message.objects.filter(room=self.room).count(), 26,
                         "Message count should increment by one after posting.")


class TestRoomCreateView(TestCase):
    def setUp(self):
        """Set up a user for testing room creation."""
        self.client = Client()
        self.user = User.objects.create_user(username="creator", password="testpass")

    def test_room_create(self):
        """Test that RoomCreateView creates a new room with the logged-in user as owner."""
        self.client.login(username="creator", password="testpass")
        post_data = {
            'name': 'New Room',
            'guests': [],  # No guests initially.
            'is_owner_only_editable': True,
            'is_publicly_visible': False,
        }
        response = self.client.post(reverse('room-create'), data=post_data)
        self.assertEqual(response.status_code, 302)
        room = Room.objects.get(name='New Room')
        self.assertEqual(room.owner, self.user,
                         "The room owner should be the logged-in user.")


class TestRoomUpdateView(TestCase):
    def setUp(self):
        """Set up an owner and guest user and a room for testing updates."""
        self.client = Client()
        self.owner = User.objects.create_user(username="owner", password="testpass")
        self.guest = User.objects.create_user(username="guest", password="testpass")
        self.room = Room.objects.create(owner=self.owner, name="Room to Update", is_owner_only_editable=True)
        self.room.guests.add(self.guest)

    def test_room_update_by_owner(self):
        """Test that the room owner can update room details."""
        self.client.login(username="owner", password="testpass")
        post_data = {
            'name': 'Updated Room Name',
            'guests': [self.guest.pk],
            'is_owner_only_editable': True,
            'is_publicly_visible': False,
        }
        response = self.client.post(reverse('room-update', kwargs={'pk': self.room.pk}), data=post_data)
        self.assertEqual(response.status_code, 302)
        updated_room = Room.objects.get(pk=self.room.pk)
        self.assertEqual(updated_room.name, 'Updated Room Name')

    def test_room_update_by_guest_without_permission(self):
        """Test that a guest without permissions cannot update the room (should return 404)."""
        self.client.login(username="guest", password="testpass")
        post_data = {
            'name': 'Unauthorized Update Attempt',
            'guests': [self.guest.pk],
            'is_owner_only_editable': True,
            'is_publicly_visible': False,
        }
        response = self.client.post(reverse('room-update', kwargs={'pk': self.room.pk}), data=post_data)
        self.assertEqual(response.status_code, 404)


class TestRoomToggleFavouriteView(TestCase):
    def setUp(self):
        """Set up a user and room for testing toggling favourites."""
        self.client = Client()
        self.user = User.objects.create_user(username="favuser", password="testpass")
        self.room = Room.objects.create(owner=self.user, name="Fav Room")
        # Ensure the room's favourited_by list starts empty.
        self.room.favorited_by.clear()

    def test_toggle_favourite_add(self):
        """Test that posting to the toggle favourite view adds the user to room.favorited_by."""
        self.client.login(username="favuser", password="testpass")
        response = self.client.post(reverse('room-toggle-favourite', kwargs={'pk': self.room.pk}))
        self.assertEqual(response.status_code, 302)
        self.assertIn(self.user, self.room.favorited_by.all())

    def test_toggle_favourite_remove(self):
        """Test that posting to the toggle favourite view removes the user if already favourited."""
        self.room.favorited_by.add(self.user)
        self.client.login(username="favuser", password="testpass")
        response = self.client.post(reverse('room-toggle-favourite', kwargs={'pk': self.room.pk}))
        self.assertEqual(response.status_code, 302)
        self.assertNotIn(self.user, self.room.favorited_by.all())


class TestRoomJoinView(TestCase):
    def setUp(self):
        """Set up a public room for testing room-join functionality."""
        self.client = Client()
        self.owner = User.objects.create_user(username="owner", password="testpass")
        self.joiner = User.objects.create_user(username="joiner", password="testpass")
        self.room = Room.objects.create(owner=self.owner, name="Joinable Room", is_publicly_visible=True)

    def test_join_room(self):
        """Test that a user can join a public room if they are neither owner nor already a guest."""
        self.client.login(username="joiner", password="testpass")
        response = self.client.post(reverse('room-join', kwargs={'pk': self.room.pk}))
        self.assertEqual(response.status_code, 302)
        self.assertIn(self.joiner, self.room.guests.all())

    def test_join_room_not_public(self):
        """Test that a user cannot join a room that is not publicly visible."""
        self.room.is_publicly_visible = False
        self.room.save()
        self.client.login(username="joiner", password="testpass")
        response = self.client.post(reverse('room-join', kwargs={'pk': self.room.pk}))
        self.assertEqual(response.status_code, 302)
        self.assertNotIn(self.joiner, self.room.guests.all())


class TestRoomLeaveView(TestCase):
    def setUp(self):
        """Set up an owner, guest, and a room for testing room leave functionality."""
        self.client = Client()
        self.owner = User.objects.create_user(username="owner", password="testpass")
        self.guest = User.objects.create_user(username="guest", password="testpass")
        self.room = Room.objects.create(owner=self.owner, name="Room to Leave", is_publicly_visible=True)
        self.room.guests.add(self.guest)
        self.room.favorited_by.add(self.owner)

    def test_guest_leave_room(self):
        """Test that a guest can leave the room."""
        self.client.login(username="guest", password="testpass")
        response = self.client.post(reverse('room-leave', kwargs={'pk': self.room.pk}))
        self.assertEqual(response.status_code, 302)
        self.assertNotIn(self.guest, self.room.guests.all())

    def test_owner_leave_room_with_transfer(self):
        """
        Test that when the room owner leaves and there is a guest,
        ownership is transferred and the original owner is removed from favourites.
        """
        self.client.login(username="owner", password="testpass")
        response = self.client.post(reverse('room-leave', kwargs={'pk': self.room.pk}))
        self.assertEqual(response.status_code, 302)
        updated_room = Room.objects.get(pk=self.room.pk)
        self.assertEqual(updated_room.owner, self.guest)
        self.assertNotIn(self.guest, updated_room.guests.all(),
                         "New owner should be removed from the guests list after transfer.")
        self.assertNotIn(self.owner, updated_room.favorited_by.all())

    def test_owner_leave_room_no_guests(self):
        """
        Test that when the room owner leaves and there are no guests,
        the room is deleted.
        """
        self.room.guests.clear()
        self.client.login(username="owner", password="testpass")
        response = self.client.post(reverse('room-leave', kwargs={'pk': self.room.pk}))
        self.assertEqual(response.status_code, 302)
        with self.assertRaises(Room.DoesNotExist):
            Room.objects.get(pk=self.room.pk)


class TestRoomDeleteView(TestCase):
    def setUp(self):
        """Set up a room for testing deletion."""
        self.client = Client()
        self.owner = User.objects.create_user(username="owner", password="testpass")
        self.room = Room.objects.create(owner=self.owner, name="Deletable Room")

    def test_owner_can_delete_room(self):
        """Test that the room owner can delete the room."""
        self.client.login(username="owner", password="testpass")
        response = self.client.post(reverse('room-delete', kwargs={'pk': self.room.pk}))
        self.assertEqual(response.status_code, 302)
        with self.assertRaises(Room.DoesNotExist):
            Room.objects.get(pk=self.room.pk)

    def test_non_owner_cannot_delete_room(self):
        """Test that a non-owner attempting to delete the room receives a 404."""
        non_owner = User.objects.create_user(username="nonowner", password="testpass")
        self.client.login(username="nonowner", password="testpass")
        response = self.client.post(reverse('room-delete', kwargs={'pk': self.room.pk}))
        self.assertEqual(response.status_code, 404)


class TestProtectedMediaView(TestCase):
    def setUp(self):
        """Set up a room with an image message to test access via ProtectedMediaView."""
        self.client = Client()
        self.owner = User.objects.create_user(username="owner", password="testpass")
        self.guest = User.objects.create_user(username="guest", password="testpass")
        self.other = User.objects.create_user(username="other", password="testpass")
        self.room = Room.objects.create(owner=self.owner, name="Room with Image")
        self.room.guests.add(self.guest)
        # Create a dummy image (a minimal GIF header).
        self.image_content = b'\x47\x49\x46\x38\x39\x61'
        self.image_file = SimpleUploadedFile("test.gif", self.image_content, content_type="image/gif")
        self.message = Message.objects.create(
            room=self.room, sender=self.owner,
            content="Image message", image=self.image_file
        )
        # Write a physical media file to disk.
        self.media_file_path = Path(settings.MEDIA_ROOT) / self.message.image.name
        self.media_file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.media_file_path, 'wb') as f:
            f.write(self.image_content)

    def test_owner_can_access_media(self):
        """Test that the room owner can access the protected media file."""
        self.client.login(username="owner", password="testpass")
        response = self.client.get(reverse('protected-media', kwargs={'message_id': self.message.pk}))
        # Ensure to close the response to free the file handle.
        response.close()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get('Content-Type'), 'image/gif')

    def test_guest_can_access_media(self):
        """Test that a room guest can access the protected media file."""
        self.client.login(username="guest", password="testpass")
        response = self.client.get(reverse('protected-media', kwargs={'message_id': self.message.pk}))
        response.close()
        self.assertEqual(response.status_code, 200)

    def test_unauthorized_user_cannot_access_media(self):
        """Test that an unauthorized user is forbidden from accessing the protected media file."""
        self.client.login(username="other", password="testpass")
        response = self.client.get(reverse('protected-media', kwargs={'message_id': self.message.pk}))
        response.close()
        self.assertEqual(response.status_code, 403)

    def tearDown(self):
        """Clean up the dummy media file after tests."""
        # On Windows the file may be in use, so we catch PermissionError.
        if self.media_file_path.exists():
            try:
                self.media_file_path.unlink()
            except PermissionError:
                pass