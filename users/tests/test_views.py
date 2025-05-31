from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User


class TestCustomLoginView(TestCase):
    def setUp(self):
        """Set up a test user and relevant URLs for testing login functionality."""
        self.login_url = reverse('login')
        self.home_url = reverse('home')
        self.user = User.objects.create_user(username='testuser', password='testpass123')

    def test_login_page_renders_correctly(self):
        """Test that the login page returns 200 and uses the correct template."""
        response = self.client.get(self.login_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/login.html')

    def test_login_redirects_authenticated_user(self):
        """Test that an authenticated user is redirected to home when accessing the login page."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(self.login_url)
        self.assertRedirects(response, self.home_url)

    def test_successful_login_redirects_to_home(self):
        """Test that valid credentials log the user in and redirect to the home page."""
        response = self.client.post(self.login_url, {
            'username': 'testuser', 
            'password': 'testpass123'
        })
        self.assertRedirects(response, self.home_url)
        self.assertTrue(response.wsgi_request.user.is_authenticated)

    def test_failed_login_rerenders_login_page(self):
        """Test that invalid credentials rerender the login page with errors."""
        response = self.client.post(self.login_url, {
            'username': 'testuser', 
            'password': 'wrongpassword'
        })
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/login.html')
        self.assertFalse(response.wsgi_request.user.is_authenticated)


class TestRegisterView(TestCase):
    def setUp(self):
        """Set up the register and home URLs for testing registration functionality."""
        self.register_url = reverse('register')
        self.home_url = reverse('home')

    def test_registration_page_renders_correctly(self):
        """Test that the registration page returns 200 and uses the correct template."""
        response = self.client.get(self.register_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/register.html')

    def test_registration_redirects_authenticated_user(self):
        """Test that an authenticated user is redirected to home when accessing the registration page."""
        user = User.objects.create_user(username='testuser', password='testpass123')
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(self.register_url)
        self.assertRedirects(response, self.home_url)

    def test_successful_registration_creates_user_and_redirects_to_home(self):
        """Test that posting valid data creates a user, logs them in, and redirects to home."""
        response = self.client.post(self.register_url, {
            'username': 'newuser',
            'password1': 'strongPassword321',
            'password2': 'strongPassword321',
        })
        self.assertTrue(User.objects.filter(username='newuser').exists())
        self.assertRedirects(response, self.home_url)
        self.assertTrue(response.wsgi_request.user.is_authenticated)

    def test_failed_registration_rerenders_registration_page(self):
        """Test that invalid data rerenders the registration page with form errors."""
        response = self.client.post(self.register_url, {
            'username': '',
            'password1': 'mismatch',
            'password2': 'another',
        })
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/register.html')
        self.assertFalse(User.objects.filter(username='').exists())
        self.assertContains(response, 'The two password fields didn’t match.')
