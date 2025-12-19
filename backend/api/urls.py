from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'menu', views.MenuItemViewSet)
router.register(r'promo', views.PromoViewSet)
router.register(r'booking', views.BookingViewSet)
router.register(r'users', views.UserViewSet, basename='user')

urlpatterns = [
    path('', include(router.urls)),
    path('token/', views.TokenView.as_view(), name='token'),
    path('register/', views.RegisterView.as_view(), name='register'),
]