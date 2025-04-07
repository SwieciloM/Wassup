from django.test import TestCase, RequestFactory
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django_select2.forms import Select2MultipleWidget

from chat.forms import RoomForm, MessageForm
from chat.models import Room, Message
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image
import io


def create_test_image_file(filename='test_image.jpg', size=(50, 50), color=(256,0,0)):
    """Return a SimpleUploadedFile containing a valid image."""
    file_obj = io.BytesIO()
    image = Image.new("RGB", size, color)
    image.save(file_obj, 'JPEG')
    file_obj.seek(0)
    return SimpleUploadedFile(filename, file_obj.read(), content_type='image/jpeg')


class TestRoomForm(TestCase):
    def setUp(self):
        """Set up a couple of users and a request for testing the form."""
        self.user1 = User.objects.create_user(username='user1', password='testpass')
        self.user2 = User.objects.create_user(username='user2', password='testpass')

        self.factory = RequestFactory()
        self.request = self.factory.get('/')  # An HTTP GET request
        self.request.user = self.user1  # Simulated logged-in user

    def test_form_fields(self):
        """Test whether RoomForm has the correct fields and uses UserSelectWidget for 'guests'."""
        form = RoomForm(request=self.request)

        self.assertIn('name', form.fields)
        self.assertIn('guests', form.fields)
        self.assertIn('is_owner_only_editable', form.fields)
        self.assertIn('is_publicly_visible', form.fields)
        self.assertTrue(
            isinstance(form.fields['guests'].widget, Select2MultipleWidget),
            "Expected 'guests' field to use a Select2-based widget."
        )

    def test_request_passed_to_widget(self):
        """Test whether the widget on 'guests' field receives the 'request' object."""
        form = RoomForm(request=self.request)
        self.assertEqual(form.fields['guests'].widget.request, self.request,
                         "Widget should store the same request passed into the form.")

    def test_widget_excludes_current_user(self):
        """Test whether the widget's queryset excludes the logged-in user."""
        form = RoomForm(request=self.request)
        widget_queryset = form.fields['guests'].widget.get_queryset()
        self.assertNotIn(self.user1, widget_queryset,
                         "Widget's queryset should exclude the form's request.user.")
        self.assertIn(self.user2, widget_queryset,
                      "Widget's queryset should include other users.")


class TestMessageForm(TestCase):
    def setUp(self):
        """Prepare a user and a room in case we need them for referencing message creation."""
        self.user = User.objects.create_user(username='user1', password='testpass')
        self.room = Room.objects.create(
            name="Test Room",
            owner=self.user,
            is_owner_only_editable=True,
            is_publicly_visible=False,
        )

    def test_form_fields(self):
        """Test whether MessageForm has 'content' and 'image' fields."""
        form = MessageForm()
        self.assertEqual(list(form.fields.keys()), ['content', 'image'],
                         "MessageForm should only have 'content' and 'image' fields.")

    def test_form_valid_content_only(self):
        """Test whether the form is valid with only 'content' set."""
        form_data = {'content': 'Hello!'}
        form_files = {}
        form = MessageForm(data=form_data, files=form_files)
        self.assertTrue(form.is_valid(), "Form should be valid if 'content' is provided.")

    def test_form_valid_image_only(self):
        """Test whether the form is valid with only 'image' set."""
        image_file = create_test_image_file()  # This is now a valid JPEG
        form = MessageForm(data={}, files={'image': image_file})
        self.assertTrue(form.is_valid(), "Form should be valid if 'image' is provided.")

    def test_form_invalid_no_content_no_image(self):
        """Test whether the form raises a ValidationError if neither content nor image is provided."""
        form_data = {}
        form_files = {}
        form = MessageForm(data=form_data, files=form_files)
        self.assertFalse(form.is_valid(), "Form should be invalid if neither content nor image is provided.")
        self.assertIn("Please enter text or choose an image to upload.", form.errors['__all__'],
                      "Expected validation error message for empty content and image.")
