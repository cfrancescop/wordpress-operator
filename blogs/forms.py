from django import forms

class SignupForm(forms.Form):
    blog_name = forms.CharField(
        label='Blog Name', 
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your blog name'})
    )
    # Add more fields as needed (e.g., email, password)
