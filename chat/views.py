from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from django.db.models import Q
from django.views.generic import DetailView
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy

from .models import Room, Message
from .forms import MessageForm


class RoomListView(LoginRequiredMixin, ListView):
    """Displays list of saved rooms for the logged-in user."""
    model = Room
    context_object_name = 'rooms'

    def get_context_data(self, **kwargs):
        """Adds filtered rooms to the context."""
        context = super().get_context_data(**kwargs)
        
        # Rooms the user is connected to (owner or guest)
        connected_rooms = Room.objects.filter(
            Q(owner=self.request.user) | Q(guests=self.request.user)
        ).distinct()
        
        # Public rooms that the user is not connected to
        public_rooms = Room.objects.filter(is_publicly_visible=True).exclude(
            id__in=connected_rooms.values_list('id', flat=True)
        ).distinct()
        
        context['connected_rooms'] = connected_rooms
        context['public_rooms'] = public_rooms
        return context


class RoomDetailView(LoginRequiredMixin, DetailView):
    model = Room
    context_object_name = 'room'

    def get_queryset(self):
        """Only return lobby owned by the current user."""
        return Room.objects.filter(Q(owner=self.request.user) | Q(guests=self.request.user)).distinct()

    def get_context_data(self, **kwargs):
        """
        Pass the room, the messages, and a fresh message form
        to the template context.
        """
        context = super().get_context_data(**kwargs)
        room = self.object

        # Fetch the 20 most recent messages; show oldest at the top
        recent_messages = room.messages.all()[:20]
        context['messages'] = reversed(recent_messages)

        # Provide an empty form for GET requests
        context['message_form'] = MessageForm()
        return context

    def post(self, request, *args, **kwargs):
        """
        Handle creation of a new Message on POST.
        """
        self.object = self.get_object()  # The current Room
        form = MessageForm(request.POST, request.FILES)

        if form.is_valid():
            # Use form.save(commit=False) so we can attach the room/sender
            new_message = form.save(commit=False)
            new_message.room = self.object
            new_message.sender = request.user
            new_message.save()

            # Redirect back to the same room detail
            return redirect('room', pk=self.object.pk)
        else:
            # If form is invalid, re-render the page with the form errors
            context = self.get_context_data()
            context['message_form'] = form
            return self.render_to_response(context)


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
