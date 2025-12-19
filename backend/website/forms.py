from django import forms
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
import re
from datetime import date
from api.models import User, Booking


class LoginForm(forms.Form):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Email'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Пароль'
        })
    )

    def clean_email(self):
        email = self.cleaned_data.get('email', '').strip()
        if not email:
            raise ValidationError('Введите email')
        try:
            validate_email(email)
        except ValidationError:
            raise ValidationError('Некорректный email')
        return email

    def clean_password(self):
        password = self.cleaned_data.get('password', '').strip()
        if not password:
            raise ValidationError('Введите пароль')
        if len(password) < 8:
            raise ValidationError(
                'Пароль должен содержать не менее 8 символов')
        return password


class RegisterForm(UserCreationForm):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Email'
        })
    )
    first_name = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Имя'
        })
    )
    last_name = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Фамилия'
        })
    )
    phone = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '+7 (XXX) XXX-XX-XX'
        })
    )

    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name',
                  'phone', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Пароль'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Подтверждение пароля'
        })

    def clean_email(self):
        email = self.cleaned_data.get('email', '').strip().lower()
        if not email:
            raise ValidationError('Введите email')
        try:
            validate_email(email)
        except ValidationError:
            raise ValidationError('Некорректный email')
        if User.objects.filter(email=email).exists():
            raise ValidationError('Пользователь с таким email уже существует')
        return email

    def clean_phone(self):
        phone = self.cleaned_data.get('phone', '').strip()
        if phone:
            phone_pattern = r'^(\+7|7|8)?[\s\-]?\(?\d{3}\)?[\s\-]?\d{3}[\s\-]?\d{2}[\s\-]?\d{2}$'
            if not re.match(phone_pattern, phone):
                raise ValidationError(
                    'Введите корректный номер телефона РФ (+7XXXXXXXXXX, 8XXXXXXXXXX)')

            digits = re.sub(r'\D', '', phone)

            if digits.startswith('8'):
                digits = '7' + digits[1:]
            elif digits.startswith('7'):
                digits = '7' + digits[1:]
            elif len(digits) == 10:
                digits = '7' + digits

            if len(digits) != 11:
                raise ValidationError('Номер должен содержать 11 цифр')

            return f'+7{digits[1:]}'
        return phone

    def clean_first_name(self):
        first_name = self.cleaned_data.get('first_name', '').strip()
        if not first_name:
            raise ValidationError('Имя обязательно для заполнения')
        if len(first_name) < 2:
            raise ValidationError('Имя должно содержать не менее 2 символов')
        if not re.match(r'^[a-zA-Zа-яА-ЯёЁ\s\-]+$', first_name):
            raise ValidationError(
                'Имя может содержать только буквы, пробелы и дефисы')
        return first_name

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = self.cleaned_data['email']
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data.get('last_name', '')
        user.phone = self.cleaned_data.get('phone', '')
        user.role = 'user'
        user.is_active = True

        if commit:
            user.save()
        return user


class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['name', 'phone', 'email',
                  'date', 'time', 'persons', 'comment']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Имя'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+7 (XXX) XXX-XX-XX'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Email'
            }),
            'date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'time': forms.TimeInput(attrs={
                'class': 'form-control',
                'type': 'time'
            }),
            'persons': forms.NumberInput(attrs={
                'class': 'form-control'
            }),
            'comment': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Комментарий'
            }),
        }

    def clean_date(self):
        booking_date = self.cleaned_data.get('date')
        if booking_date:
            today = date.today()
            if booking_date < today:
                raise ValidationError('Нельзя бронировать на прошедшую дату')
            max_date = date(today.year + 1, today.month, today.day)
            if booking_date > max_date:
                raise ValidationError('Максимальный срок бронирования - 1 год')
        return booking_date

    def clean_time(self):
        booking_time = self.cleaned_data.get('time')
        if booking_time:
            from datetime import time
            opening_time = time(8, 0)
            closing_time = time(23, 0)
            if booking_time < opening_time or booking_time > closing_time:
                raise ValidationError('Мы работаем с 8:00 до 23:00')
        return booking_time

    def clean_phone(self):
        phone = self.cleaned_data.get('phone', '').strip()
        if not phone:
            raise ValidationError('Телефон обязателен для связи')

        phone_pattern = r'^(\+7|7|8)?[\s\-]?\(?\d{3}\)?[\s\-]?\d{3}[\s\-]?\d{2}[\s\-]?\d{2}$'
        if not re.match(phone_pattern, phone):
            raise ValidationError(
                'Введите корректный номер телефона РФ (+7XXXXXXXXXX, 8XXXXXXXXXX)')

        digits = re.sub(r'\D', '', phone)
        if len(digits) < 10:
            raise ValidationError('Номер слишком короткий')

        if digits.startswith('8'):
            digits = '7' + digits[1:]
        elif digits.startswith('7'):
            digits = '7' + digits[1:]
        elif len(digits) == 10:
            digits = '7' + digits

        if len(digits) != 11:
            raise ValidationError('Номер должен содержать 11 цифр')

        return f'+7{digits[1:]}'

    def clean(self):
        cleaned_data = super().clean()
        date_value = cleaned_data.get('date')
        time_value = cleaned_data.get('time')

        if date_value and time_value:
            from datetime import datetime
            booking_datetime = datetime.combine(date_value, time_value)
            current_datetime = datetime.now()

            if booking_datetime < current_datetime:
                raise ValidationError('Выбранные дата и время уже прошли')

        return cleaned_data


class ProfileUpdateForm(forms.ModelForm):
    current_password = forms.CharField(
        label='Текущий пароль (для подтверждения изменений)',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите текущий пароль'
        }),
        required=False
    )

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'phone')
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+7 (XXX) XXX-XX-XX'}),
        }

    def clean_email(self):
        email = self.cleaned_data.get('email', '').strip().lower()
        if not email:
            raise ValidationError('Email обязателен')
        if User.objects.filter(email=email).exclude(id=self.instance.id).exists():
            raise ValidationError(
                'Этот email уже используется другим пользователем')
        return email

    def clean_phone(self):
        phone = self.cleaned_data.get('phone', '').strip()
        if phone:
            phone_pattern = r'^(\+7|7|8)?[\s\-]?\(?\d{3}\)?[\s\-]?\d{3}[\s\-]?\d{2}[\s\-]?\d{2}$'
            if not re.match(phone_pattern, phone):
                raise ValidationError(
                    'Введите корректный номер телефона РФ (+7XXXXXXXXXX, 8XXXXXXXXXX)')

            digits = re.sub(r'\D', '', phone)
            if len(digits) < 10:
                raise ValidationError('Номер слишком короткий')

            if digits.startswith('8'):
                digits = '7' + digits[1:]
            elif digits.startswith('7'):
                digits = '7' + digits[1:]
            elif len(digits) == 10:
                digits = '7' + digits

            if len(digits) != 11:
                raise ValidationError('Номер должен содержать 11 цифр')

            return f'+7{digits[1:]}'
        return phone

    def clean(self):
        cleaned_data = super().clean()
        new_email = cleaned_data.get('email')
        current_password = cleaned_data.get('current_password')

        if new_email and new_email != self.instance.email:
            if not current_password:
                self.add_error('current_password',
                               'Для изменения email необходимо подтвердить текущий пароль')
            elif not self.instance.check_password(current_password):
                self.add_error('current_password', 'Неверный текущий пароль')

        return cleaned_data


class ChangePasswordForm(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name in ['old_password', 'new_password1', 'new_password2']:
            self.fields[field_name].widget.attrs.update(
                {'class': 'form-control'})


class MenuFilterForm(forms.Form):
    TYPE_CHOICES = [
        ('all', 'Все'),
        ('coffee', 'Кофе'),
        ('tea', 'Чай'),
        ('desserts', 'Десерты'),
        ('breakfast', 'Завтраки'),
    ]

    type = forms.ChoiceField(
        label='Категория',
        choices=TYPE_CHOICES,
        required=False,
        initial='all',
        widget=forms.Select(attrs={
            'class': 'form-control',
            'onchange': 'this.form.submit()'
        })
    )

    popular = forms.BooleanField(
        label='Только популярные',
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input',
            'onchange': 'this.form.submit()'
        })
    )