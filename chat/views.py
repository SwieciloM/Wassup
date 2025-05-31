from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from django.db.models import Q, Max, Exists, OuterRef
from django.views.generic import DetailView
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import FileResponse, Http404, HttpResponseForbidden
from django.urls import reverse_lazy
from django.conf import settings
from pathlib import Path

from .models import Room, Message
from .forms import MessageForm, RoomForm


class RoomListView(LoginRequiredMixin, ListView):
    """Displays the logged-in user's rooms, joined rooms, and public rooms."""
    model = Room
    context_object_name = 'rooms'

    def get_context_data(self, **kwargs):
        """Populate the context with categorized room lists."""
        context = super().get_context_data(**kwargs)

        favourited_subquery = Room.objects.filter(pk=OuterRef('pk'), favorited_by=self.request.user)

        my_rooms = Room.objects.filter(
            owner=self.request.user
        ).annotate(
            last_message_datetime=Max('messages__created_at'),
            is_favourite=Exists(favourited_subquery)
        ).order_by('-is_favourite', '-last_message_datetime', '-created_at').distinct()

        joined_rooms = Room.objects.filter(
            guests=self.request.user
        ).exclude(
            owner=self.request.user
        ).annotate(
            last_message_datetime=Max('messages__created_at'),
            is_favourite=Exists(favourited_subquery)
        ).order_by('-is_favourite', '-last_message_datetime', '-created_at').distinct()

        public_rooms = Room.objects.filter(
            is_publicly_visible=True
        ).exclude(
            Q(owner=self.request.user) | Q(guests=self.request.user)
        ).annotate(
            last_message_datetime=Max('messages__created_at'),
            is_favourite=Exists(favourited_subquery)
        ).order_by('-is_favourite', '-last_message_datetime', '-created_at').distinct()

        context['my_rooms'] = my_rooms
        context['joined_rooms'] = joined_rooms
        context['public_rooms'] = public_rooms
        return context


class RoomDetailView(LoginRequiredMixin, DetailView):
    """Displays room details and handles message submission."""
    model = Room
    context_object_name = 'room'

    def get_queryset(self):
        """Restrict access to rooms the user owns or has joined."""
        return Room.objects.filter(Q(owner=self.request.user) | Q(guests=self.request.user)).distinct()

    def get_context_data(self, **kwargs):
        """Add recent messages and message form to context."""
        context = super().get_context_data(**kwargs)
        room = self.object
        recent_messages = room.messages.all()[:20]
        context['messages'] = list(reversed(recent_messages))
        context['message_form'] = MessageForm()
        return context

    def post(self, request, *args, **kwargs):
        """Handle posting a new message in the room."""
        self.object = self.get_object()
        form = MessageForm(request.POST, request.FILES)

        if form.is_valid():
            new_message = form.save(commit=False)
            new_message.room = self.object
            new_message.sender = request.user
            new_message.save()
            return redirect('room', pk=self.object.pk)

        context = self.get_context_data()
        context['message_form'] = form
        return self.render_to_response(context)


class RoomCreateView(LoginRequiredMixin, CreateView):
    """Handles creation of a new room."""
    model = Room
    form_class = RoomForm
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        """Set the logged-in user as the room owner."""
        form.instance.owner = self.request.user
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        """Add form type to context."""
        context = super().get_context_data(**kwargs)
        context['form_type'] = 'create'
        return context

    def get_form_kwargs(self):
        """Pass request to the form instance."""
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs


class RoomUpdateView(LoginRequiredMixin, UpdateView):
    """Handles editing existing rooms."""
    model = Room
    form_class = RoomForm
    success_url = reverse_lazy('home')

    def get_queryset(self):
        """Allow edits by the owner or guests with permissions."""
        user = self.request.user
        return Room.objects.filter(Q(owner=user) | Q(is_owner_only_editable=False, guests=user)).distinct()

    def get_context_data(self, **kwargs):
        """Add form type to context."""
        context = super().get_context_data(**kwargs)
        context['form_type'] = 'update'
        return context

    def get_form_kwargs(self):
        """Pass request to the form instance."""
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs


class RoomToogleFavouriteView(LoginRequiredMixin, View):
    """Toggles favourite status for the current user."""
    def post(self, request, pk):
        room = get_object_or_404(Room, pk=pk)
        if request.user in room.favorited_by.all():
            room.favorited_by.remove(request.user)
        else:
            room.favorited_by.add(request.user)
        return redirect('home')


class RoomJoinView(LoginRequiredMixin, View):
    """Adds the current user to the room guests."""
    def post(self, request, pk):
        room = get_object_or_404(Room, pk=pk)
        if room.is_publicly_visible and request.user not in room.guests.all() and request.user != room.owner:
            room.guests.add(request.user)
        return redirect('home')


class RoomLeaveView(LoginRequiredMixin, View):
    """Handles leaving a room, and ownership transfer if needed."""
    def post(self, request, pk):
        room = get_object_or_404(Room, pk=pk)

        if request.user in room.guests.all():
            room.guests.remove(request.user)

        if request.user in room.favorited_by.all():
            room.favorited_by.remove(request.user)

        if request.user == room.owner:
            if room.guests.exists():
                new_owner = room.guests.first()
                room.owner = new_owner
                room.guests.remove(new_owner)
                room.save()
            else:
                room.delete()

        return redirect('home')


class RoomDeleteView(LoginRequiredMixin, DeleteView):
    """Handles deletion of a room by its owner."""
    model = Room
    context_object_name = 'room'
    success_url = reverse_lazy('home')

    def get_queryset(self):
        """Restrict deletion to rooms owned by the user."""
        return Room.objects.filter(owner=self.request.user)


class ProtectedMediaView(LoginRequiredMixin, View):
    """Serves image files from messages to authorized users."""

    def get(self, request, message_id):
        message = get_object_or_404(Message, pk=message_id)
        room = message.room

        # Access restricted to room owner or guests
        if request.user != room.owner and request.user not in room.guests.all():
            return HttpResponseForbidden("You do not have permission to access this resource.")

        if not message.image:
            raise Http404("No image associated with this message.")

        full_path = Path(settings.MEDIA_ROOT) / message.image.name
        if not full_path.exists():
            raise Http404("File not found on the server.")

        return FileResponse(open(full_path, 'rb'))
