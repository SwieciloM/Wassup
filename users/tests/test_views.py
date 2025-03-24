from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User


class TestCustomLoginView(TestCase):
    def setUp(self):
        """Sets up the test user and relevant URLs."""
        self.login_url = reverse('login')
        self.home_url = reverse('home')
        self.user = User.objects.create_user(username='testuser', password='testpass123')

    def test_login_page_renders_correctly(self):
        """Login page should return 200 with the correct template."""
        response = self.client.get(self.login_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/login.html')

    def test_login_redirects_authenticated_user(self):
        """Authenticated user should be redirected to home if they access the login page."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(self.login_url)
        self.assertRedirects(response, self.home_url)

    def test_successful_login_redirects_to_home(self):
        """Posting valid credentials should log the user in and redirect to home."""
        response = self.client.post(self.login_url, {
            'username': 'testuser', 
            'password': 'testpass123'
        })
        self.assertRedirects(response, self.home_url)
        self.assertTrue(response.wsgi_request.user.is_authenticated)

    def test_failed_login_rerenders_login_page(self):
        """Posting invalid credentials should rerender the login page with errors."""
        response = self.client.post(self.login_url, {
            'username': 'testuser', 
            'password': 'wrongpassword'
        })
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/login.html')
        self.assertFalse(response.wsgi_request.user.is_authenticated)


class TestRegisterView(TestCase):
    def setUp(self):
        """Sets up the register URL and home URL for use in tests."""
        self.register_url = reverse('register')
        self.home_url = reverse('home')

    def test_registration_page_renders_correctly(self):
        """Registration page should return 200 with the correct template."""
        response = self.client.get(self.register_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/register.html')

    def test_registration_redirects_authenticated_user(self):
        """Authenticated user should be redirected to home if they access the register page."""
        user = User.objects.create_user(username='testuser', password='testpass123')
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(self.register_url)
        self.assertRedirects(response, self.home_url)

    def test_successful_registration_creates_user_and_redirects_to_home(self):
        """Posting valid data should create a new user, log them in, and redirect to home."""
        response = self.client.post(self.register_url, {
            'username': 'newuser',
            'password1': 'strongPassword321',
            'password2': 'strongPassword321',
        })
        self.assertTrue(User.objects.filter(username='newuser').exists())
        self.assertRedirects(response, self.home_url)
        self.assertTrue(response.wsgi_request.user.is_authenticated)

    def test_failed_registration_rerenders_registration_page(self):
        """Posting invalid data should rerender the registration page with errors."""
        response = self.client.post(self.register_url, {
            'username': '',
            'password1': 'mismatch',
            'password2': 'another',
        })
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/register.html')
        self.assertFalse(User.objects.filter(username='').exists())
        self.assertContains(response, 'The two password fields didn’t match.')