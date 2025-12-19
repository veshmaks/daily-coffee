from django.db import models
from django.utils import timezone
from django.core.validators import RegexValidator
from django.contrib.auth.models import AbstractUser, Group


class User(AbstractUser):
    email = models.EmailField('Email', unique=True)
    phone = models.CharField('Телефон', max_length=20, blank=True,
                             validators=[RegexValidator(
                                 regex=r'^[\d\s\-\+\(\)]{7,20}$',
                                 message='Введите корректный номер телефона'
                             )])
    role = models.CharField('Роль', max_length=20, default='user')
    created_at = models.DateTimeField('Дата создания', default=timezone.now)

    groups = models.ManyToManyField(
        Group,
        verbose_name='Группы',
        blank=True,
        help_text='Группы, к которым принадлежит пользователь',
        related_name='custom_user_groups',
        related_query_name='user'
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'password']

    def __str__(self):
        name = f"{self.first_name} {self.last_name}".strip()
        return name if name else self.email

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'


class MenuItem(models.Model):
    TYPE_CHOICES = [
        ('coffee', 'Кофе'),
        ('tea', 'Чай'),
        ('desserts', 'Десерты'),
        ('breakfast', 'Завтраки'),
    ]

    name = models.CharField('Название', max_length=200)
    type = models.CharField('Тип', max_length=20,
                            choices=TYPE_CHOICES, default='coffee')
    description = models.TextField('Описание', blank=True, null=True)
    price = models.DecimalField('Цена', max_digits=10, decimal_places=2)
    image = models.ImageField(
        'Изображение', upload_to='menu_images/', blank=True, null=True)
    is_active = models.BooleanField('Активно', default=True)
    sort_order = models.IntegerField('Порядок сортировки', default=0)
    is_popular = models.BooleanField('Популярное', default=False)

    class Meta:
        db_table = 'menu'
        ordering = ['sort_order', 'name']
        verbose_name = 'Позиция меню'
        verbose_name_plural = 'Позиции меню'

    def __str__(self):
        return self.name

    @property
    def image_url(self):
        if self.image and hasattr(self.image, 'url'):
            return self.image.url

    def get_current_promos(self):
        today = timezone.now().date()
        return MenuPromo.objects.filter(
            menu_item=self,
            promo__start_date__lte=today,
            promo__end_date__gte=today,
            promo__is_active=True
        )

    @property
    def current_promo(self):
        promos = self.get_current_promos()
        return promos.first() if promos.exists() else None

    @property
    def discount_price(self):
        promo = self.current_promo
        if promo and promo.discount_percent > 0:
            discount = self.price * promo.discount_percent / 100
            return self.price - discount
        return self.price

    @property
    def has_discount(self):
        promo = self.current_promo
        if promo:
            return promo.discount_percent > 0
        return False

    @property
    def discount_percent(self):
        promo = self.current_promo
        if promo:
            return promo.discount_percent
        return 0


class Promo(models.Model):
    title = models.CharField('Заголовок', max_length=200)
    description = models.TextField('Описание')
    image = models.ImageField(
        'Изображение', upload_to='promo_images/', blank=True, null=True)
    start_date = models.DateField('Дата начала')
    end_date = models.DateField('Дата окончания')
    is_active = models.BooleanField('Активно', default=True)
    created_at = models.DateTimeField('Дата создания', default=timezone.now)

    class Meta:
        db_table = 'promo'
        verbose_name = 'Акция'
        verbose_name_plural = 'Акции'

    def __str__(self):
        return self.title


class Booking(models.Model):
    STATUS_CHOICES = [
        ('new', 'Новая'),
        ('confirmed', 'Подтверждена'),
        ('cancelled', 'Отменена'),
        ('completed', 'Завершена'),
    ]

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, db_column='user_id', null=True, blank=True)
    name = models.CharField('Имя', max_length=100, default='Гость')
    phone = models.CharField('Телефон', max_length=20, default='не указан')
    email = models.EmailField('Email', default='guest@test.com')
    date = models.DateField('Дата')
    time = models.TimeField('Время')
    persons = models.IntegerField('Количество персон')
    status = models.CharField('Статус', max_length=50,
                              choices=STATUS_CHOICES, default='new')
    comment = models.TextField('Комментарий', blank=True, null=True)
    created_at = models.DateTimeField('Дата создания', default=timezone.now)

    class Meta:
        db_table = 'bookings'
        verbose_name = 'Бронирование'
        verbose_name_plural = 'Бронирования'

    def __str__(self):
        return f"Бронь #{self.id} - {self.name}"


class MenuPromo(models.Model):
    menu_item = models.ForeignKey(
        MenuItem, on_delete=models.CASCADE, db_column='menu_id')
    promo = models.ForeignKey(
        'Promo', on_delete=models.CASCADE, db_column='promo_id')
    discount_percent = models.IntegerField('Процент скидки', default=0)
    created_at = models.DateTimeField('Дата создания', default=timezone.now)

    class Meta:
        db_table = 'menu_promo'
        unique_together = ['menu_item', 'promo']
        verbose_name = 'Меню-Акция'
        verbose_name_plural = 'Меню-Акции'

    def __str__(self):
        return f"{self.menu_item.name} - {self.promo.title}"
