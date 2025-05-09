from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('predict/', views.predict_view, name='predict'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
]