from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from .models import User, MenuItem, Promo, Booking, MenuPromo


class CustomUserAdmin(BaseUserAdmin):
    list_display = ('email', 'first_name', 'last_name', 'role',
                    'phone', 'is_staff', 'is_active', 'get_groups')
    list_filter = ('role', 'is_staff', 'is_superuser', 'is_active', 'groups')
    search_fields = ('email', 'first_name', 'last_name', 'phone')
    ordering = ('email',)

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Персональная информация'), {
         'fields': ('first_name', 'last_name', 'phone', 'role')}),
        (_('Права доступа'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        (_('Важные даты'), {
         'fields': ('last_login', 'date_joined', 'created_at')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'password1', 'password2', 'first_name', 'last_name', 'phone', 'role'),
        }),
    )

    filter_horizontal = ('groups', 'user_permissions')

    def get_groups(self, obj):
        return ", ".join([group.name for group in obj.groups.all()])
    get_groups.short_description = 'Группы'


admin.site.register(User, CustomUserAdmin)


@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'type', 'price', 'is_popular',
                    'is_active', 'sort_order')
    list_filter = ('type', 'is_active', 'is_popular')
    search_fields = ('name', 'description')
    list_editable = ('price', 'is_popular', 'is_active', 'sort_order')

    fieldsets = (
        ('Основная информация', {
         'fields': ('name', 'type', 'description', 'price')}),
        ('Изображение', {'fields': ('image',), 'classes': ('collapse',)}),
        ('Настройки отображения', {
         'fields': ('is_popular', 'is_active', 'sort_order')}),
    )


@admin.register(Promo)
class PromoAdmin(admin.ModelAdmin):
    list_display = ('title', 'start_date', 'end_date', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('title', 'description')


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone', 'date',
                    'time', 'persons', 'status')
    list_filter = ('status', 'date')
    search_fields = ('name', 'email', 'phone')


@admin.register(MenuPromo)
class MenuPromoAdmin(admin.ModelAdmin):
    list_display = ('menu_item', 'promo', 'discount_percent')
    list_filter = ('promo',)
