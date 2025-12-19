from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.authentication import TokenAuthentication, SessionAuthentication
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth import authenticate
from .models import User, MenuItem, Promo, Booking
from .serializers import (UserSerializer, MenuItemSerializer,
                          PromoSerializer, BookingSerializer, TokenSerializer)
from .permissions import IsStaffOrReadOnly, IsSuperUser


class TokenView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = TokenSerializer(data=request.data)
        if serializer.is_valid():
            user = authenticate(username=serializer.data['email'],
                                password=serializer.data['password'])
            if user:
                token, _ = Token.objects.get_or_create(user=user)
                return Response({'token': token.key, 'user': UserSerializer(user).data})
            return Response({'error': 'Неверные данные'}, status=400)
        return Response(serializer.errors, status=400)


class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        if not email or not password:
            return Response({'error': 'Нет email или пароля'}, status=400)

        if User.objects.filter(email=email).exists():
            return Response({'error': 'Email уже есть'}, status=400)

        try:
            user = User.objects.create_user(
                email=email,
                username=email,
                password=password,
                first_name=request.data.get('first_name', ''),
                last_name=request.data.get('last_name', ''),
                phone=request.data.get('phone', ''),
                role='user'
            )

            token = Token.objects.create(user=user)
            return Response({'token': token.key, 'user': UserSerializer(user).data})

        except Exception as e:
            return Response({'error': str(e)}, status=400)


class MenuItemViewSet(viewsets.ModelViewSet):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    permission_classes = [IsStaffOrReadOnly]

    def get_queryset(self):
        qs = MenuItem.objects.all()
        item_type = self.request.query_params.get('type')
        if item_type:
            qs = qs.filter(type=item_type)
        if not self.request.user.is_staff:
            qs = qs.filter(is_active=True)
        return qs.order_by('sort_order', 'name')


class PromoViewSet(viewsets.ModelViewSet):
    queryset = Promo.objects.all()
    serializer_class = PromoSerializer
    permission_classes = [IsStaffOrReadOnly]

    def get_queryset(self):
        qs = Promo.objects.all()
        if not self.request.user.is_staff:
            from django.utils import timezone
            today = timezone.now().date()
            qs = qs.filter(is_active=True, end_date__gte=today)
        return qs.order_by('-start_date')


class BookingViewSet(viewsets.ModelViewSet):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_staff or self.request.user.is_superuser:
            return Booking.objects.all()
        return Booking.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    authentication_classes = [TokenAuthentication, SessionAuthentication]
    permission_classes = [IsSuperUser]
