from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from django.views.generic import DetailView
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy

from .models import Room


class RoomListView(LoginRequiredMixin, ListView):
    """Displays list of saved rooms for the logged-in user."""
    model = Room
    context_object_name = 'rooms'

    def get_context_data(self, **kwargs):
        """Adds filtered rooms to the context."""
        context = super().get_context_data(**kwargs)
        context['rooms'] = context['rooms'].filter(owner=self.request.user)

        return context


class RoomDetailView(LoginRequiredMixin, DetailView):
    pass


class RoomCreateView(LoginRequiredMixin, CreateView):
    """Handles room creation."""
    model = Room
    fields = ['name', 'guests', 'is_owner_only_editable', 'is_publicly_visible']
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        """Associates the created room with the logged-in user."""
        form.instance.owner = self.request.user
        return super(RoomCreateView, self).form_valid(form)
    
    def get_context_data(self, **kwargs):
        """Adds a form type identifier to the context."""
        context = super().get_context_data(**kwargs)
        context['form_type'] = 'create'
        return context


class RoomUpdateView(LoginRequiredMixin, UpdateView):
    """Handles room updates."""
    model = Room
    fields = ['name', 'guests', 'is_owner_only_editable', 'is_publicly_visible']
    success_url = reverse_lazy('home')

    def get_queryset(self):
        """Only return rooms owned by the current user."""
        return Room.objects.filter(owner=self.request.user)

    def get_context_data(self, **kwargs):
        """Adds a form type identifier to the context."""
        context = super().get_context_data(**kwargs)
        context['form_type'] = 'update'
        return context


class RoomToogleFavouriteView(LoginRequiredMixin, View):
    """Toggles the favourite status of a room."""
    def post(self, request, pk):
        task = get_object_or_404(Room, pk=pk, owner=request.user)
        task.is_completed = not task.is_completed
        task.save()
        return redirect('home')


class RoomDeleteView(LoginRequiredMixin, DeleteView):
    """Handles room deletion."""
    model = Room
    context_object_name = 'room'
    success_url = reverse_lazy('home')

    def get_queryset(self):
        """Only return rooms owned by the current user."""
        return Room.objects.filter(owner=self.request.user)
