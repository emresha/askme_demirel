from django import forms

class LoginForm(forms.Form):
    username = forms.CharField(max_length=150)
    password = forms.CharField(max_length=128)
    

class SignUpForm(forms.Form):
    username = forms.CharField(max_length=32)
    email = forms.EmailField()
    password = forms.CharField(max_length=32)
    password_confirm = forms.CharField(max_length=32)
    picture = forms.ImageField(required=False)
    
class QuestionForm(forms.Form):
    title = forms.CharField(max_length=255)
    description = forms.CharField()
    tags = forms.CharField(required=True, max_length=255)
    
class CommentForm(forms.Form):
    content = forms.CharField()
    
class SettingsForm(forms.Form):
    username = forms.CharField(max_length=32)
    email = forms.EmailField()
    picture = forms.ImageField(required=False)