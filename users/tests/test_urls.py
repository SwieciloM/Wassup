from django.test import SimpleTestCase
from django.urls import reverse, resolve
from users.views import CustomLoginView, RegisterView
from django.contrib.auth.views import LogoutView


class TestUrlResolution(SimpleTestCase):
    def test_login_url_resolution(self):
        """Test whether the login URLPattern is resolving to the CustomLoginView."""
        url = reverse('login')
        self.assertEqual(resolve(url).func.view_class, CustomLoginView)

    def test_logout_url_resolution(self):
        """Test whether the logout URLPattern is resolving to the LogoutView."""
        url = reverse('logout')
        self.assertEqual(resolve(url).func.view_class, LogoutView)

    def test_register_url_resolution(self):
        """Test whether the register URLPattern is resolving to the RegisterView."""
        url = reverse('register')
        self.assertEqual(resolve(url).func.view_class, RegisterView)


class TestUrlReversal(SimpleTestCase):
    def test_login_url_reversal(self):
        """Test whether the reversed login URLPattern is '/'."""
        url = reverse('login')
        self.assertEqual(url, '/')

    def test_logout_url_reversal(self):
        """Test whether the reversed logout URLPattern is '/logout/'."""
        url = reverse('logout')
        self.assertEqual(url, '/logout/')

    def test_register_url_reversal(self):
        """Test whether the reversed register URLPattern is '/register/'."""
        url = reverse('register')
        self.assertEqual(url, '/register/')