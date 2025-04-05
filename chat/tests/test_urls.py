from django.test import SimpleTestCase
from django.urls import reverse, resolve
from chat.views import RoomListView, RoomDetailView, RoomCreateView, RoomToogleFavouriteView, RoomLeaveView, RoomUpdateView, RoomDeleteView, RoomJoinView, ProtectedMediaView


class TestUrlResolution(SimpleTestCase):
    def test_home_url_resolution(self):
        """Test whether the home URLPattern is resolving to the RoomListView."""
        url = reverse('home')
        self.assertEqual(resolve(url).func.view_class, RoomListView)

    def test_room_url_resolution(self):
        """Test whether the room URLPattern is resolving to the RoomDetailView."""
        url = reverse('room', args=[1])
        self.assertEqual(resolve(url).func.view_class, RoomDetailView)

    def test_room_create_url_resolution(self):
        """Test whether the room-create URLPattern is resolving to the RoomCreateView."""
        url = reverse('room-create')
        self.assertEqual(resolve(url).func.view_class, RoomCreateView)

    def test_room_update_url_resolution(self):
        """Test whether the room-update URLPattern is resolving to the RoomUpdateView."""
        url = reverse('room-update', args=[1])
        self.assertEqual(resolve(url).func.view_class, RoomUpdateView)

    def test_room_delete_url_resolution(self):
        """Test whether the room-delete URLPattern is resolving to the RoomDeleteView."""
        url = reverse('room-delete', args=[1])
        self.assertEqual(resolve(url).func.view_class, RoomDeleteView)

    def test_room_toggle_favourite_url_resolution(self):
        """Test whether the room-toggle-favourite URLPattern is resolving to the RoomToogleFavouriteView."""
        url = reverse('room-toggle-favourite', args=[1])
        self.assertEqual(resolve(url).func.view_class, RoomToogleFavouriteView)
    
    def test_room_leave_url_resolution(self):
        """Test whether the room-leave URLPattern is resolving to the RoomLeaveView."""
        url = reverse('room-leave', args=[1])
        self.assertEqual(resolve(url).func.view_class, RoomLeaveView)
    
    def test_room_join_url_resolution(self):
        """Test whether the room-join URLPattern is resolving to the RoomJoinView."""
        url = reverse('room-join', args=[1])
        self.assertEqual(resolve(url).func.view_class, RoomJoinView)
    
    def test_protected_media_url_resolution(self):
        """Test whether the protected-media URLPattern is resolving to the ProtectedMediaView."""
        url = reverse('protected-media', args=[1])
        self.assertEqual(resolve(url).func.view_class, ProtectedMediaView)


class TestUrlReversal(SimpleTestCase):
    def test_home_url_reversal(self):
        """Test whether the reversed home URLPattern is '/my-rooms/'."""
        url = reverse('home')
        self.assertEqual(url, '/my-rooms/')

    def test_room_url_reversal(self):
        """Test whether the reversed room URLPattern is '/my-rooms/room/1/'."""
        url = reverse('room', args=[1])
        self.assertEqual(url, '/my-rooms/room/1/')

    def test_room_create_url_reversal(self):
        """Test whether the reversed room-create URLPattern is '/my-rooms/room-create/'."""
        url = reverse('room-create')
        self.assertEqual(url, '/my-rooms/room-create/')

    def test_room_update_url_reversal(self):
        """Test whether the reversed room-update URLPattern is '/my-rooms/room-update/1/'."""
        url = reverse('room-update', args=[1])
        self.assertEqual(url, '/my-rooms/room-update/1/')

    def test_room_delete_url_reversal(self):
        """Test whether the reversed room-delete URLPattern is '/my-rooms/room-delete/1/'."""
        url = reverse('room-delete', args=[1])
        self.assertEqual(url, '/my-rooms/room-delete/1/')

    def test_room_toggle_favourite_url_reversal(self):
        """Test whether the reversed room-toggle-favourite URLPattern is '/my-rooms/room-toggle-favourite/1/'."""
        url = reverse('room-toggle-favourite', args=[1])
        self.assertEqual(url, '/my-rooms/room-toggle-favourite/1/')

    def test_room_leave_url_reversal(self):
        """Test whether the reversed room-leave URLPattern is '/my-rooms/room-leave/1/'."""
        url = reverse('room-leave', args=[1])
        self.assertEqual(url, '/my-rooms/room-leave/1/')

    def test_room_join_url_reversal(self):
        """Test whether the reversed room-join URLPattern is '/my-rooms/room-join/1/'."""
        url = reverse('room-join', args=[1])
        self.assertEqual(url, '/my-rooms/room-join/1/')

    def test_protected_media_url_reversal(self):
        """Test whether the reversed protected-media URLPattern is '/my-rooms/media/1/'."""
        url = reverse('protected-media', args=[1])
        self.assertEqual(url, '/my-rooms/media/1/')
