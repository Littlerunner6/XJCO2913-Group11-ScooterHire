from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count
from .models import Scooter, Order
import datetime

def admin_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_superuser:
            return render(request, 'error.html', {'msg': '无管理员权限'})
        return view_func(request, *args, **kwargs)
    return login_required(wrapper)

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
    
    new_order = Order.objects.create(
        user=request.user,
        scooter=scooter,
        hire_period=hire_period,
        total_price=total_price
    )
    
    scooter.is_available = False
    scooter.save()
    
    return render(request, 'order_success.html', {
        'order': new_order
    })

@login_required
def pay_order(request, order_id):
    try:
        order = Order.objects.get(id=order_id, user=request.user)
    except Order.DoesNotExist:
        return render(request, 'error.html', {'msg': '订单不存在！'})
    
    if order.pay_status == 'paid':
        return render(request, 'error.html', {'msg': '该订单已支付，无需重复支付！'})
    if order.pay_status == 'cancelled':
        return render(request, 'error.html', {'msg': '该订单已取消，无法支付！'})
    
    if request.method == 'POST':
        order.pay_status = 'paid'
        order.save()
        return render(request, 'pay_success.html', {
            'order': order
        })
    
    return render(request, 'pay_order.html', {
        'order': order
    })

@login_required
def my_orders(request):
    orders = Order.objects.filter(user=request.user).order_by('-order_time')
    return render(request, 'my_orders.html', {
        'username': request.user.username,
        'orders': orders
    })

@login_required
def cancel_order(request, order_id):
    if request.method != 'POST':
        return render(request, 'error.html', {'msg': '该页面仅支持表单提交，请勿直接访问！'})
    
    try:
        order = Order.objects.get(
            id=order_id, 
            user=request.user, 
            pay_status='unpaid'
        )
    except Order.DoesNotExist:
        return render(request, 'error.html', {'msg': '无法取消该订单（订单不存在/已支付/已取消）！'})
    
    order.pay_status = 'cancelled'
    order.save()
    scooter = order.scooter
    scooter.is_available = True
    scooter.save()
    
    return render(request, 'cancel_success.html', {
        'order': order
    })

@admin_required
def weekly_income(request):
    today = datetime.date.today()
    monday = today - datetime.timedelta(days=today.weekday())
    sunday = monday + datetime.timedelta(days=6)
    start_datetime = datetime.datetime.combine(monday, datetime.time.min)
    end_datetime = datetime.datetime.combine(sunday, datetime.time.max)

    income_stats = Order.objects.filter(
        pay_status='paid',
        order_time__gte=start_datetime,
        order_time__lte=end_datetime
    ).values('hire_period').annotate(
        order_count=Count('id'),
        total_income=Sum('total_price')
    ).order_by('hire_period')

    all_periods = ['1h', '4h', '1d', '1w']
    stat_data = []
    max_order_count = 0

    for period in all_periods:
        period_stat = next((item for item in income_stats if item['hire_period'] == period), None)
        order_count = period_stat['order_count'] if period_stat else 0
        total_income = period_stat['total_income'] if period_stat else 0.00

        if order_count > max_order_count:
            max_order_count = order_count

        stat_data.append({
            'period': period,
            'period_name': dict(Order.HIRE_PERIOD_CHOICES).get(period, "未知时长"),
            'order_count': order_count,
            'total_income': round(float(total_income), 2),
            'is_hot': order_count == max_order_count and max_order_count > 0
        })

    total_weekly_income = sum([item['total_income'] for item in stat_data])

    return render(request, 'admin/weekly_income.html', {
        'monday': monday.strftime('%Y-%m-%d'),
        'sunday': sunday.strftime('%Y-%m-%d'),
        'stat_data': stat_data,
        'total_weekly_income': round(total_weekly_income, 2),
        'has_data': total_weekly_income > 0
    })