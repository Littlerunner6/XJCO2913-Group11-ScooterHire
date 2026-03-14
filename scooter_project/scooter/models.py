from django.db import models
from django.contrib.auth.models import User

class Scooter(models.Model):
    name = models.CharField(max_length=50, verbose_name="编号", unique=True)
    price_1h = models.FloatField(default=0.0, verbose_name="1小时价格")
    price_4h = models.FloatField(default=0.0, verbose_name="4小时价格")
    price_1d = models.FloatField(default=0.0, verbose_name="1天价格")
    price_1w = models.FloatField(default=0.0, verbose_name="1周价格")
    is_available = models.BooleanField(default=True, verbose_name="是否可用")

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = "滑板车"
        verbose_name_plural = "滑板车"

class Order(models.Model):
    HIRE_PERIOD_CHOICES = (
        ('1h', '1小时'),
        ('4h', '4小时'),
        ('1d', '1天'),
        ('1w', '1周'),
    )
    ORDER_STATUS_CHOICES = (
        ('unpaid', '未支付'),
        ('paid', '已支付'),
        ('cancelled', '已取消'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="下单用户")
    scooter = models.ForeignKey(Scooter, on_delete=models.CASCADE, verbose_name="租赁滑板车")
    hire_period = models.CharField(default='1h', max_length=2, choices=HIRE_PERIOD_CHOICES, verbose_name="租赁时长")
    total_price = models.FloatField(default=0.0, verbose_name="订单总价")
    order_time = models.DateTimeField(auto_now_add=True, verbose_name="下单时间")
    pay_status = models.CharField(default='unpaid', max_length=10, choices=ORDER_STATUS_CHOICES, verbose_name="订单状态")

    def __str__(self):
        return f"{self.user.username} - {self.scooter.name} - {self.order_time}"
    
    @property
    def hire_period_cn(self):
        return dict(self.HIRE_PERIOD_CHOICES).get(self.hire_period, "未知时长")
    
    @property
    def pay_status_cn(self):
        return dict(self.ORDER_STATUS_CHOICES).get(self.pay_status, "未知状态")
    
    class Meta:
        verbose_name = "订单"
        verbose_name_plural = "订单"