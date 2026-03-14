from django.db import models
from django.contrib.auth.models import User

class Scooter(models.Model):
    name = models.CharField(max_length=50, verbose_name="编号")
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
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="下单用户")
    scooter = models.ForeignKey(Scooter, on_delete=models.CASCADE, verbose_name="租赁滑板车")
    order_time = models.DateTimeField(auto_now_add=True, verbose_name="下单时间")
    is_paid = models.BooleanField(default=False, verbose_name="是否支付")

    def __str__(self):
        return f"{self.user.username} - {self.scooter.name} - {self.order_time}"
    
    class Meta:
        verbose_name = "订单"
        verbose_name_plural = "订单"