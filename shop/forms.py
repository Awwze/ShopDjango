from django import forms
from .models import Product, Review,  Comment, Category
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm


class ProductForm(forms.ModelForm):
    category = forms.ModelChoiceField(queryset=Category.objects.all(), required=True, label='Category')

    class Meta:
        model = Product
        fields = ['name', 'description', 'price', 'image', 'category', 'stock']


class UserLoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'}),
        max_length=150
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}),
        max_length=128
    )

class UserRegistrationForm(AuthenticationForm):
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
