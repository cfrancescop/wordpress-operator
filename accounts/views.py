from django.shortcuts import render, redirect
from django.contrib.auth import login
from .forms import CustomUserCreationForm

def signup(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # Log the user in after signup
            return redirect('home')  # Replace 'home' with your desired URL
    else:
        form = CustomUserCreationForm()
    return render(request, 'accounts/signup.html', {'form': form})
