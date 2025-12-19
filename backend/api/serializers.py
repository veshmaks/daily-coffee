from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import User, MenuItem, Promo, Booking, MenuPromo


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'first_name', 'last_name', 'phone', 'role')


class MenuItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = MenuItem
        fields = '__all__'


class PromoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Promo
        fields = '__all__'


class BookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = '__all__'
        read_only_fields = ('user', 'created_at', 'status')

    def create(self, validated_data):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            validated_data['user'] = request.user
        return super().create(validated_data)


class MenuPromoSerializer(serializers.ModelSerializer):
    class Meta:
        model = MenuPromo
        fields = '__all__'


class TokenSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()
