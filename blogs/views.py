from django.shortcuts import render, redirect

from blogs.models import Blog
from .forms import SignupForm

def signup(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            # Process the form data (e.g., save to database)
            blog_name = form.cleaned_data['blog_name']
            # ... your logic here ...
            blog = Blog(title=blog_name, hostname=blog_name.lower().replace(" ", "") + ".example.com") 
            blog.save()
            return render(request, 'blogs/signup_success.html', {'blog_hostname': blog.hostname})

    else:
        form = SignupForm()
    return render(request, 'blogs/signup.html', {'form': form})

def signup_success(request):
    """Renders a success page after signup, including a link to the blog's hostname."""
    blog_hostname = request.session.get('blog_hostname', None)  # Retrieve from session
    return render(request, 'blogs/signup_success.html', {'blog_hostname': blog_hostname})

def landing_page(request):
    return render(request, 'blogs/landing.html')