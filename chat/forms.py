from django import forms
from django_select2 import forms as s2forms
from django.contrib.auth.models import User
from .models import Message, Room


class UserSelectWidget(s2forms.ModelSelect2MultipleWidget):
    """A custom widget for selecting multiple Users via django-select2 with AJAX search."""
    model = User
    search_fields = ['username__icontains']

    def __init__(self, *args, **kwargs):
        self.request = None  # Placeholder for request context
        super().__init__(*args, **kwargs)
        self.attrs.update({
            'data-placeholder': 'Type username...',  # Custom placeholder
            'style': 'width: 100%;',  # Custom width
        })

    def get_queryset(self):
        """Excludes the currently logged-in user from the queryset."""
        queryset = super().get_queryset()
        if self.request and self.request.user.is_authenticated:
            return queryset.exclude(id=self.request.user.id)
        return queryset

    def build_attrs(self, base_attrs, extra_attrs=None):
        """Ensures widget receives request data."""
        attrs = super().build_attrs(base_attrs, extra_attrs)
        attrs['data-minimum-input-length'] = 1  # Requires at least 1 character before search
        return attrs


class RoomForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        """Pass request to the widget to exclude the current user."""
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)
        self.fields['guests'].widget.request = self.request  # Pass request to widget

    class Meta:
        model = Room
        fields = ['name', 'guests', 'is_owner_only_editable', 'is_publicly_visible']
        widgets = {
            'guests': UserSelectWidget,
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