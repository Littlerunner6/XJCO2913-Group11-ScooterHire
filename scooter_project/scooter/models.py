from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User

class Scooter(models.Model):
    name = models.CharField(max_length=50, verbose_name="编号", unique=True)
    price_per_hour = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=10.00,
        verbose_name="基础小时单价（¥/小时）"
    )
    min_hire_hours = models.PositiveIntegerField(default=1, verbose_name="最低起租小时数")
    is_available = models.BooleanField(default=True, verbose_name="是否可用")

    def __str__(self):
        return self.name
    
    def clean_fields(self, exclude=None):
        super().clean_fields(exclude=exclude)
        if self.price_per_hour < 0:
            raise ValidationError("小时单价不能为负数！")
        if self.min_hire_hours < 1:
            raise ValidationError("最低起租小时数不能小于1！")
    
    class Meta:
        verbose_name = "滑板车"
        verbose_name_plural = "滑板车"

class Order(models.Model):
    ORDER_STATUS_CHOICES = (
        ('unpaid', '未支付'),
        ('paid', '已支付'),
        ('cancelled', '已取消'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="下单用户")
    scooter = models.ForeignKey(Scooter, on_delete=models.CASCADE, verbose_name="租赁滑板车")
    hire_period = models.PositiveIntegerField(default=1, verbose_name="租赁小时数")
    total_price = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=0.00,
        verbose_name="订单总价"
    )
    order_time = models.DateTimeField(auto_now_add=True, verbose_name="下单时间")
    pay_status = models.CharField(default='unpaid', max_length=10, choices=ORDER_STATUS_CHOICES, verbose_name="订单状态")

    def __str__(self):
        return f"{self.user.username} - {self.scooter.name} - {self.order_time}"
    
    def clean_fields(self, exclude=None):
        super().clean_fields(exclude=exclude)
        if self.total_price < 0:
            raise ValidationError("订单总价不能为负数！")
    
    @property
    def hire_period_cn(self):
        return f"{self.hire_period} 小时"
    
    @property
    def pay_status_cn(self):
        return dict(self.ORDER_STATUS_CHOICES).get(self.pay_status, "未知状态")
    
    class Meta:
        verbose_name = "订单"
        verbose_name_plural = "订单"

class Card(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="用户")
    card_last4 = models.CharField(max_length=4, verbose_name="卡号后4位")
    bank_name = models.CharField(max_length=50, verbose_name="银行名称")
    is_default = models.BooleanField(default=False, verbose_name="设为默认")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="添加时间")

    def __str__(self):
        return f"{self.bank_name} (*{self.card_last4})"

    class Meta:
        verbose_name = "银行卡"
        verbose_name_plural = "银行卡"