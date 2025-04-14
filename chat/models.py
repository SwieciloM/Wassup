from django.db import models
from django.contrib.auth.models import User


class Room(models.Model):
    """Model representing a chat room associated with owner."""
    name = models.CharField(max_length=30)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="owned_rooms")
    guests = models.ManyToManyField(User, blank=True, related_name="guest_rooms")
    favorited_by = models.ManyToManyField(User, blank=True, related_name="favorite_rooms")
    is_owner_only_editable = models.BooleanField(default=True)
    is_publicly_visible = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} (owner: {self.owner.username})"

    class Meta:
        """Meta options for the Room model."""
        ordering = ["-created_at"]
        verbose_name = "Room"
        verbose_name_plural = "Rooms"


class Message(models.Model):
    """Model representing single, user's message in the chat."""
    room = models.ForeignKey("Room", on_delete=models.CASCADE, related_name="messages")
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sent_messages")
    content = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='message_images/', blank=True, null=True, default=None)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.content and not self.image:
            raise ValueError("Message must contain text or image.")
        super().save(*args, **kwargs)

    def __str__(self):
        if self.image:
            return f"User '{self.sender.username}' in room '{self.room.name}' at {self.created_at.strftime('%Y-%m-%d %H:%M:%S')}: [image]"
        else:
            return f"User '{self.sender.username}' in room '{self.room.name}' at {self.created_at.strftime('%Y-%m-%d %H:%M:%S')}: {self.content[:15]}"

    class Meta:
        """Meta options for Message model."""
        ordering = ["-created_at"]
        verbose_name = "Message"
        verbose_name_plural = "Messages"
    
