from django.shortcuts import render
from django.contrib.auth.views import LoginView
from .forms import CustomUserCreationForm
from django.views.generic.edit import FormView
from django.contrib.auth import login
from django.shortcuts import redirect
from django.urls import reverse_lazy


class CustomLoginView(LoginView):
    """Handles user login with redirection for authenticated users."""
    template_name = 'users/login.html'
    fields = '__all__'
    redirect_authenticated_user = True

    def get_success_url(self):
        """Redirect to the 'tasks' page upon successful login."""
        return reverse_lazy('home')


class RegisterView(FormView):
    """Handles user registration and automatic login."""
    template_name = 'users/register.html'
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        """Save the user and log them in if the form is valid."""
        user = form.save()
        if user is not None:
            login(self.request, user)
        return super(RegisterView, self).form_valid(form)
    
    def get(self, *args, **kwargs):
        """Redirect authenticated users to 'tasks' or show the form."""
        if self.request.user.is_authenticated:
            return redirect('home')
        return super().get(self.request, *args, **kwargs)
