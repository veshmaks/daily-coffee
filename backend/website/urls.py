from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('menu/', views.menu_page, name='menu'),
    path('booking/', views.booking_page, name='booking'),
    path('promo/', views.promo_page, name='promo'),
    path('contacts/', views.contacts_page, name='contacts'),
    path('login/', views.login_page, name='login'),
    path('register/', views.register_page, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_page, name='profile'),
]