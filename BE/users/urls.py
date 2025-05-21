# BE/users/urls.py
from django.urls import path
from .views import RegisterView, LoginView, UserInfoView, LogoutView, UpdateProfileView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),  # Add this line
    path('me/', UserInfoView.as_view(), name='user-info'),
    path('update-profile/', UpdateProfileView.as_view(), name='update-profile'),
]