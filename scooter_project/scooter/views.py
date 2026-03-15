from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseBadRequest
from .models import Scooter, Order

@login_required
def index(request):
    scooters = Scooter.objects.filter(is_available=True).order_by('name')

    return render(request, 'index.html', {
        'username': request.user.username,
        'scooters': scooters,
    })

@login_required
def create_order_page(request, scooter_id):
    scooter = get_object_or_404(Scooter, id=scooter_id)
    if not scooter.is_available:
        return render(request, 'error.html', {'msg': '该滑板车不可预订！'})
    return render(request, 'create_order.html', {'scooter': scooter})

@login_required
def submit_order(request):
    if request.method != 'POST':
        return render(request, 'error.html', {'msg': '该页面仅支持表单提交，请勿直接访问！'})
    
    scooter_id = request.POST.get('scooter_id')
    hire_period = request.POST.get('hire_period')
    
    if not scooter_id or not hire_period:
        return render(request, 'error.html', {'msg': '请选择租赁时长！'})
    scooter = get_object_or_404(Scooter, id=scooter_id)
    if not scooter.is_available:
        return render(request, 'error.html', {'msg': '该滑板车不可预订！'})
    
    match hire_period:
        case '1h':
            total_price = scooter.price_1h
        case '4h':
            total_price = scooter.price_4h
        case '1d':
            total_price = scooter.price_1d
        case '1w':
            total_price = scooter.price_1w
        case _:
            return render(request, 'error.html', {'msg': '无效的租赁时长！'})
    
    Order.objects.create(
        user=request.user,
        scooter=scooter,
        hire_period=hire_period,
        total_price=total_price
    )
    
    scooter.is_available = False
    scooter.save()
    
    return render(request, 'order_success.html', {
        'scooter_name': scooter.name,
        'hire_period': dict(Order.HIRE_PERIOD_CHOICES)[hire_period],
        'total_price': total_price
    })
