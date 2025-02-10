from django import forms
from .models import Message


class MessageForm(forms.ModelForm):
    """
    A form that supports sending a text message or an image (stored in a BinaryField).
    """
    # We use a FileField (or ImageField) for file uploads
    # so that we can process it manually in the view.
    uploaded_image = forms.FileField(required=False)

    class Meta:
        model = Message
        fields = ['content', 'uploaded_image']  # 'uploaded_image' is not on the model, but is a temporary form field

    def clean(self):
        """
        Ensure that at least one field (content or uploaded_image) is provided.
        The model-level validation also enforces this, but it’s good to do so
        at the form level for user-friendly error messages.
        """
        cleaned_data = super().clean()
        content = cleaned_data.get('content')
        image = cleaned_data.get('uploaded_image')
        
        if not content and not image:
            raise forms.ValidationError("Please enter text or choose an image to upload.")

        return cleaned_data
