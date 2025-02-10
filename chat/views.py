from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
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
        context['rooms'] = context['rooms'].filter(owner=self.request.user)

        return context


class RoomDetailView(LoginRequiredMixin, DetailView):
    model = Room
    context_object_name = 'room'

    def get_context_data(self, **kwargs):
        """
        Pass the room, the messages, and a fresh message form
        to the template context.
        """
        context = super().get_context_data(**kwargs)
        room = self.object  # or self.get_object()

        # Fetch recent messages. Using slicing + reorder
        # so that the newest appear at the bottom.
        recent_messages = room.messages.all()[:20]  # limited to last 20
        context['messages'] = reversed(recent_messages)

        # Empty form on GET request
        context['message_form'] = MessageForm()

        return context

    def post(self, request, *args, **kwargs):
        """
        Handle creation of a new Message on POST.
        """
        self.object = self.get_object()
        form = MessageForm(request.POST, request.FILES)

        if form.is_valid():
            # We have at least text or an uploaded image
            new_message = Message(
                room=self.object,
                sender=request.user,
                content=form.cleaned_data.get('content', '')
            )

            # If there's an image in the request, read it into the binary field
            uploaded_image = form.cleaned_data.get('uploaded_image')
            if uploaded_image:
                new_message.image_blob = uploaded_image.read()

            # Save the message
            new_message.save()

            # Redirect back to same room detail
            return redirect('room', pk=self.object.pk)
        else:
            # If form invalid, re-render the page with errors
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
