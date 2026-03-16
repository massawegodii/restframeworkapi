from django.urls import path
from .views import get_all_users, login_user, register_user

urlpatterns = [

    path('register', register_user, name='register'),
    
    path('login', login_user, name='login-user'),
    
    path('all-users/', get_all_users, name='get-all-users'),

]