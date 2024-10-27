from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Review, Comment

class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'text']

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text', 'rating']
        widgets = {
            'rating': forms.RadioSelect(choices=[(i, i) for i in range(1, 6)]),  # Радиокнопки для рейтинга
            'text': forms.Textarea(attrs={'rows': 3}),
        }
