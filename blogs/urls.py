from django.urls import path
from . import views

urlpatterns = [
    # ... other URL patterns ...
    path('signup/', views.signup, name='signup'),
    path('signup/success/', views.signup_success, name='signup_success'),
    path('', views.landing_page, name='landing_page'),
]