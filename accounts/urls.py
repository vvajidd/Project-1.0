from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register , name="register"),
    path('login/', views.login , name="login"),
    path('logout/', views.logout , name="logout"),
    

    #email verification
    path('activate/<uidb64>/<token>/', views.activate, name="activate"),
    

    # D A S H B O A R S 
    path('profile/', views.dashboard, name="dashboard"),
    path('edit_profile/', views.edit_profile, name="edit_profile"),
    path('orders/', views.orders, name="orders"),
    path('changePassword/', views.changePassword, name="changePassword"),
    path('add_address/', views.add_address, name="add_address"),
]