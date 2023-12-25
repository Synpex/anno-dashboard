from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from ..models.profile_model import UserProfile

class CustomUserCreationForm(UserCreationForm):
    # Additional fields from UserProfile
    telephone = forms.CharField(max_length=20, required=False)
    picture = forms.ImageField(required=False)

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2', 'telephone', 'picture')

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
            UserProfile.objects.create(user=user, telephone=self.cleaned_data['telephone'], picture=self.cleaned_data['picture'])
        return user
