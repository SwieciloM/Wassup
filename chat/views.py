from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from django.db.models import Q, Max, Exists, OuterRef
from django.views.generic import DetailView
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy

from .models import Room, Message
from .forms import MessageForm, RoomForm


class RoomListView(LoginRequiredMixin, ListView):
    """Displays categorized rooms for the logged-in user."""
    model = Room
    context_object_name = 'rooms'

    def get_context_data(self, **kwargs):
        """Adds categorized rooms with last message datetime and favourite flag to the context."""
        context = super().get_context_data(**kwargs)

        # Create a subquery that checks if the room is favorited by the current user
        favourited_subquery = Room.objects.filter(pk=OuterRef('pk'), favorited_by=self.request.user)
        
        # Rooms where the user is the owner
        my_rooms = Room.objects.filter(
            owner=self.request.user
        ).annotate(
            last_message_datetime=Max('messages__created_at'),
            is_favourite=Exists(favourited_subquery)
        ).order_by('-is_favourite', '-last_message_datetime', '-created_at').distinct()

        # Rooms where the user is a guest (exclude rooms where the user is also the owner)
        joined_rooms = Room.objects.filter(
            guests=self.request.user
        ).exclude(
            owner=self.request.user
        ).annotate(
            last_message_datetime=Max('messages__created_at'),
            is_favourite=Exists(favourited_subquery)
        ).order_by('-is_favourite', '-last_message_datetime', '-created_at').distinct()

        # Public rooms that the user is neither the owner nor a guest
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
    form_class = RoomForm
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        """Associates the created room with the logged-in user."""
        form.instance.owner = self.request.user
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        """Adds a form type identifier to the context."""
        context = super().get_context_data(**kwargs)
        context['form_type'] = 'create'
        return context

    def get_form_kwargs(self):
        """Pass request to the form."""
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs


class RoomUpdateView(LoginRequiredMixin, UpdateView):
    """Handles room updates."""
    model = Room
    form_class = RoomForm
    success_url = reverse_lazy('home')

    def get_queryset(self):
        """Return rooms owned by the current user or in which the guest has editing rights."""
        user = self.request.user
        return Room.objects.filter(Q(owner=user) | Q(is_owner_only_editable=False, guests=user)).distinct()

    def get_context_data(self, **kwargs):
        """Adds a form type identifier to the context."""
        context = super().get_context_data(**kwargs)
        context['form_type'] = 'update'
        return context
    
    def get_form_kwargs(self):
        """Pass request to the form."""
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs


class RoomToogleFavouriteView(LoginRequiredMixin, View):
    """Toggles the favourite status of a room for the current user."""
    def post(self, request, pk):
        room = get_object_or_404(Room, pk=pk)
        if request.user in room.favorited_by.all():
            room.favorited_by.remove(request.user)
        else:
            room.favorited_by.add(request.user)
        return redirect('home')


class RoomJoinView(LoginRequiredMixin, View):
    """Adds current user to room's participants list."""
    def post(self, request, pk):
        room = get_object_or_404(Room, pk=pk)
        if room.is_publicly_visible and request.user not in room.guests.all() and request.user != room.owner:
            room.guests.add(request.user)
        return redirect('home')


class RoomLeaveView(LoginRequiredMixin, View):
    """Removes current user from room's participants list."""
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
    """Handles room deletion."""
    model = Room
    context_object_name = 'room'
    success_url = reverse_lazy('home')

    def get_queryset(self):
        """Only return rooms owned by the current user."""
        return Room.objects.filter(owner=self.request.user)
