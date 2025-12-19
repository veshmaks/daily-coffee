from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.utils import timezone
from api.models import MenuItem, Promo, Booking
from website.forms import (
    LoginForm, RegisterForm, BookingForm,
    ProfileUpdateForm, ChangePasswordForm, MenuFilterForm
)


def home(request):
    try:
        popular_items = MenuItem.objects.filter(
            is_active=True,
            is_popular=True
        ).order_by('sort_order', 'name')[:6]

        today = timezone.now().date()
        current_promos = Promo.objects.filter(
            is_active=True,
            end_date__gte=today
        ).order_by('-start_date')[:3]

    except Exception as e:
        popular_items = []
        current_promos = []

    return render(request, 'index.html', {
        'popular_items': popular_items,
        'current_promos': current_promos,
        'today': today,
    })


def menu_page(request):
    try:
        form = MenuFilterForm(request.GET or None)
        menu_items = MenuItem.objects.filter(is_active=True)

        if form.is_valid():
            item_type = form.cleaned_data.get('type')
            popular_only = form.cleaned_data.get('popular')

            if item_type and item_type != 'all':
                menu_items = menu_items.filter(type=item_type)

            if popular_only:
                menu_items = menu_items.filter(is_popular=True)

        menu_items = menu_items.order_by('sort_order', 'name')

    except Exception:
        menu_items = []
        form = MenuFilterForm()

    return render(request, 'menu.html', {
        'menu_items': menu_items,
        'form': form,
    })


def booking_page(request):
    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            try:
                booking = form.save(commit=False)
                if request.user.is_authenticated:
                    booking.user = request.user
                booking.status = 'new'
                booking.save()

                messages.success(
                    request, f'Бронирование создано! Номер: {booking.id}')
                return redirect('booking')

            except Exception as e:
                messages.error(request, f'Ошибка: {str(e)}')
    else:
        initial = {}
        if request.user.is_authenticated:
            user = request.user
            initial.update({
                'name': f"{user.first_name} {user.last_name}".strip() or user.username,
                'email': user.email,
                'phone': user.phone or '',
            })
        form = BookingForm(initial=initial)

    return render(request, 'booking.html', {'form': form})


def promo_page(request):
    try:
        today = timezone.now().date()
        promos = Promo.objects.filter(
            is_active=True,
            end_date__gte=today
        ).order_by('-start_date')
    except Exception:
        promos = []

    return render(request, 'promo.html', {'promos': promos})


def contacts_page(request):
    return render(request, 'contacts.html')


def login_page(request):
    if request.user.is_authenticated:
        messages.info(request, 'Вы уже вошли')
        return redirect('home')

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']

            try:
                user = authenticate(username=email, password=password)

                if user is not None:
                    if user.is_active:
                        login(request, user)
                        messages.success(request, f'Добро пожаловать!')
                        next_url = request.GET.get('next', 'home')
                        return redirect(next_url)
                    else:
                        messages.error(request, 'Аккаунт деактивирован')
                else:
                    messages.error(request, 'Неверные данные')

            except Exception as e:
                messages.error(request, f'Ошибка: {str(e)}')
    else:
        form = LoginForm()

    return render(request, 'login.html', {'form': form})


def register_page(request):
    if request.user.is_authenticated:
        messages.info(request, 'Вы уже вошли')
        return redirect('home')

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    user = form.save()
                    login(request, user)
                    messages.success(request, 'Регистрация успешна!')
                    return redirect('home')

            except Exception as e:
                messages.error(request, f'Ошибка: {str(e)}')
    else:
        form = RegisterForm()

    return render(request, 'register.html', {'form': form})


def logout_view(request):
    if request.user.is_authenticated:
        logout(request)
        messages.success(request, 'Вы вышли')
    return redirect('home')


@login_required
def profile_page(request):
    bookings = Booking.objects.filter(
        user=request.user).order_by('-date', '-time')
    profile_form = ProfileUpdateForm(instance=request.user)
    password_form = ChangePasswordForm(request.user)

    return render(request, 'profile.html', {
        'bookings': bookings,
        'profile_form': profile_form,
        'password_form': password_form,
    })
