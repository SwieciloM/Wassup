from django import forms
from .models import Message


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