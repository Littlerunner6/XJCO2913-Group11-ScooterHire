from django.contrib import admin
from .models import Scooter, Order

@admin.register(Scooter)
class ScooterAdmin(admin.ModelAdmin):
    list_display = ('name', 'price_per_hour', 'min_hire_hours', 'is_available')
    search_fields = ('name',)
    list_filter = ('is_available',)
    ordering = ('name',)
    fieldsets = (
        ('基础信息', {
            'fields': ('name', 'is_available')
        }),
        ('租赁价格配置', {
            'fields': ('price_per_hour', 'min_hire_hours')
        }),
    )

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'scooter', 'hire_period_cn', 'total_price', 'pay_status_cn', 'order_time')
    search_fields = ('scooter__name', 'user__username')
    list_filter = ('pay_status', 'hire_period')
    ordering = ('-order_time',)
    readonly_fields = ('order_time',)