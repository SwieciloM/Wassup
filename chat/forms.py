from django import forms
from django_select2.forms import ModelSelect2MultipleWidget
from django.contrib.auth.models import User
from .models import Message, Room


class UserSelect2MultipleWidget(ModelSelect2MultipleWidget):
    """A custom widget for selecting multiple Users via django-select2 with AJAX search."""
    model = User
    search_fields = [
        'username__icontains',
        'first_name__icontains',
        'last_name__icontains',
    ]
    attrs = {
        'data-width': '300px',           # or '100%' for full width
        'data-placeholder': 'Select guests...',
    }
    # Optional: Additional attributes for controlling minimum input length, placeholders, etc.
    # attrs = {
    #     'data-minimum-input-length': 1,
    #     'data-placeholder': 'Search users...',
    # }

class RoomForm(forms.ModelForm):
    class Meta:
        model = Room
        fields = ['name', 'guests', 'is_owner_only_editable', 'is_publicly_visible']
        widgets = {
            'guests': UserSelect2MultipleWidget,
        }


class MessageForm(forms.ModelForm):
    """
    A form that supports sending a text message or an image, 
    stored in an ImageField on the Message model.
    """
    class Meta:
        model = Message
        fields = ['content', 'image']  # Directly use the ImageField name
    
    def clean(self):
        """
        Ensure that at least one field (content or image) is provided.
        """
        cleaned_data = super().clean()
        content = cleaned_data.get('content')
        image = cleaned_data.get('image')
        
        if not content and not image:
            raise forms.ValidationError("Please enter text or choose an image to upload.")
        
        return cleaned_data