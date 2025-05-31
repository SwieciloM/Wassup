from django import forms
from django_select2 import forms as s2forms
from django.contrib.auth.models import User
from .models import Message, Room


class UserSelectWidget(s2forms.ModelSelect2MultipleWidget):
    """Widget for selecting multiple users with AJAX search."""

    model = User
    search_fields = ['username__icontains']

    def __init__(self, *args, **kwargs):
        """Initialize widget and set custom attributes."""
        self.request = None
        super().__init__(*args, **kwargs)
        self.attrs.update({
            'data-placeholder': 'Type username...',
            'style': 'width: 100%;',
        })

    def get_queryset(self):
        """Return users excluding the current user."""
        queryset = super().get_queryset()
        if self.request and self.request.user.is_authenticated:
            return queryset.exclude(id=self.request.user.id)
        return queryset

    def build_attrs(self, base_attrs, extra_attrs=None):
        """Add custom widget attributes."""
        attrs = super().build_attrs(base_attrs, extra_attrs)
        attrs['data-minimum-input-length'] = 1
        return attrs


class RoomForm(forms.ModelForm):
    """Form for creating or updating chat rooms."""

    def __init__(self, *args, **kwargs):
        """Pass request to the guests widget to exclude current user."""
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)
        self.fields['guests'].widget.request = self.request

    class Meta:
        model = Room
        fields = ['name', 'guests', 'is_owner_only_editable', 'is_publicly_visible']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': "Type room name..."}),
            'guests': UserSelectWidget,
        }


class MessageForm(forms.ModelForm):
    """Form for sending a text or image message."""

    class Meta:
        model = Message
        fields = ['content', 'image']

    def clean(self):
        """Validate that content or image is provided."""
        cleaned_data = super().clean()
        content = cleaned_data.get('content')
        image = cleaned_data.get('image')

        if not content and not image:
            raise forms.ValidationError("Please enter text or choose an image to upload.")
        return cleaned_data
