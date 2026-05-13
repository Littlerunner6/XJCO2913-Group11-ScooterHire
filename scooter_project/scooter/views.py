from django import forms
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.db.models import Sum, Count
from .models import Scooter, Order, Card, Feedback
from django.core.mail import send_mail
from django.conf import settings
from django.core.serializers.json import DjangoJSONEncoder
from threading import Thread
import datetime, json

def admin_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_superuser:
            return render(request, 'error.html', {'msg': '无管理员权限'})
        return view_func(request, *args, **kwargs)
    return login_required(wrapper)

def is_staff(user):
    return user.is_staff

class RegisterForm(forms.ModelForm):
    username = forms.CharField(label="用户名")
    email = forms.EmailField(label="邮箱", required=True)
    password1 = forms.CharField(label="密码", widget=forms.PasswordInput)
    password2 = forms.CharField(label="确认密码", widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ["username", "email"] 

    def clean_username(self):
        username = self.cleaned_data.get("username")
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("用户名已存在")
        return username
    
    def clean_password1(self):
        pwd = self.cleaned_data.get("password1")

        if len(pwd) < 8:
            raise forms.ValidationError("密码长度不能小于8位")
        if not any(c.isalpha() for c in pwd):
            raise forms.ValidationError("密码必须包含字母")
        if not any(c.isdigit() for c in pwd):
            raise forms.ValidationError("密码必须包含数字")

        return pwd

    def clean_password2(self):
        pwd1 = self.cleaned_data.get("password1")
        pwd2 = self.cleaned_data.get("password2")
        if pwd1 and pwd2 != pwd1:
            raise forms.ValidationError("两次输入的密码不一致")
        return pwd2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user

def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('index')
    else:
        form = RegisterForm()
    return render(request, 'registration/register.html', {'form': form})

@login_required
def index(request):
    scooters = Scooter.objects.filter(is_available=True).order_by('name')

    scooters_json = json.dumps(
        list(scooters.values('id', 'name', 'address', 'latitude', 'longitude')),
        cls=DjangoJSONEncoder
    )

    return render(request, 'index.html', {
        'username': request.user.username,
        'scooters': scooters,
        'scooters_json': scooters_json
    })

@login_required
def create_order_page(request, scooter_id):
    scooter = get_object_or_404(Scooter, id=scooter_id)
    if not scooter.is_available:
        return render(request, 'error.html', {'msg': '该滑板车不可预订！'})
    return render(request, 'order/create_order.html', {'scooter': scooter})

def send_confirmation_email(order):
    subject = "滑板车预订确认"
    message = f"""
你好 {order.user.username}：

你已成功预订电动滑板车！
订单编号：{order.id}
滑板车编号：{order.scooter.name}
租赁时长：{order.hire_period} 小时
订单总价：¥{order.total_price}
下单时间：{order.order_time.strftime('%Y-%m-%d %H:%M')}

请尽快完成支付。
"""
    send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[order.user.email],
        fail_silently=True,
    )

@login_required
def submit_order(request):
    if request.method != 'POST':
        return render(request, 'error.html', {'msg': '该页面仅支持表单提交，请勿直接访问！'})
    
    scooter_id = request.POST.get('scooter_id')
    hire_period = request.POST.get('hire_period')
    
    if not scooter_id or not hire_period:
        return render(request, 'error.html', {'msg': '请选择租赁时长！'})
    
    try:
        hire_period = int(hire_period)
    except:
        return render(request, 'error.html', {'msg': '小时数必须是数字'})
    
    scooter = get_object_or_404(Scooter, id=scooter_id)
    if not scooter.is_available:
        return render(request, 'error.html', {'msg': '该滑板车不可预订！'})
    
    if hire_period < scooter.min_hire_hours:
        return render(request, 'error.html', {
            'msg': f'最低起租 {scooter.min_hire_hours} 小时'
        })

    total_price = scooter.price_per_hour * hire_period

    new_order = Order.objects.create(
        user=request.user,
        scooter=scooter,
        hire_period=hire_period,
        total_price=total_price
    )
    
    scooter.is_available = False
    scooter.save()
    
    Thread(target=send_confirmation_email, args=(new_order,)).start()

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
    
    return render(request, 'order/pay_order.html', {
        'order': order
    })

@login_required
def my_orders(request):
    orders = Order.objects.filter(user=request.user).order_by('-order_time')
    return render(request, 'order/my_orders.html', {
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

    STANDARD_PERIODS = [
        ('1h', '1小时档', 1, 4),
        ('4h', '4小时档', 4, 24),
        ('1d', '1天档(24h)', 24, 168),
        ('1w', '1周档(168h)', 168, 9999),
    ]
    all_period_keys = [p[0] for p in STANDARD_PERIODS]

    paid_orders = Order.objects.filter(
        pay_status='paid',
        order_time__gte=start_datetime,
        order_time__lte=end_datetime
    )

    stat_data = []
    max_order_count = 0
    for period_key, period_name, min_h, max_h in STANDARD_PERIODS:
        period_orders = paid_orders.filter(
            hire_period__gte=min_h,
            hire_period__lt=max_h
        )
        
        order_count = period_orders.count()
        total_income = period_orders.aggregate(Sum('total_price'))['total_price__sum'] or 0.00
        
        total_income = round(float(total_income), 2)
        
        if order_count > max_order_count:
            max_order_count = order_count
        
        stat_data.append({
            'period': period_key,
            'period_name': period_name,
            'order_count': order_count,
            'total_income': total_income,
            'is_hot': order_count == max_order_count and max_order_count > 0
        })
    
    total_weekly_income = sum([item['total_income'] for item in stat_data])
    total_weekly_income = round(total_weekly_income, 2)

    return render(request, 'admin/weekly_income.html', {
        'monday': monday.strftime('%Y-%m-%d'),
        'sunday': sunday.strftime('%Y-%m-%d'),
        'stat_data': stat_data,
        'total_weekly_income': round(total_weekly_income, 2),
        'has_data': total_weekly_income > 0
    })

@login_required
def card_list(request):
    cards = Card.objects.filter(user=request.user).order_by('-is_default', '-created_at')
    return render(request, 'card/list.html', {'cards': cards})

@login_required
def card_add(request):
    if request.method == 'POST':
        card_num = request.POST.get('card_num', '').strip()
        bank_name = request.POST.get('bank_name', '').strip()

        if len(card_num) < 4:
            return render(request, 'card/add.html', {'msg': '卡号至少4位'})

        last4 = card_num[-4:]

        Card.objects.create(
            user=request.user,
            card_last4=last4,
            bank_name=bank_name
        )
        return redirect('card_list')

    return render(request, 'card/add.html')

@login_required
def card_delete(request, card_id):
    if request.method == 'POST':
        card = get_object_or_404(Card, id=card_id, user=request.user)
        card.delete()
    return redirect('card_list')

@login_required
def set_default_card(request, card_id):
    if request.method == 'POST':
        Card.objects.filter(user=request.user).update(is_default=False)
        card = get_object_or_404(Card, id=card_id, user=request.user)
        card.is_default = True
        card.save()
    return redirect('card_list')

def send_guest_booking_email(order):
    subject = "滑板车预订确认（代下单）"
    message = f"""
您好 {order.guest_name}：

员工已为您代预订滑板车！
订单编号：{order.id}
滑板车编号：{order.scooter.name}
租赁时长：{order.hire_period} 小时

感谢使用！
"""
    send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[order.guest_email],
        fail_silently=True,
    )

@login_required
@user_passes_test(is_staff)  # 仅员工可访问
def staff_create_booking(request):
    if request.method == "POST":
        guest_name = request.POST.get("guest_name")
        guest_email = request.POST.get("guest_email")
        scooter_id = request.POST.get('scooter_id')
        hire_period = request.POST.get('hire_period')
        
        if not scooter_id or not hire_period:
            return render(request, 'error.html', {'msg': '请选择租赁时长！'})
        
        try:
            hire_period = int(hire_period)
        except:
            return render(request, 'error.html', {'msg': '小时数必须是数字'})
        
        scooter = get_object_or_404(Scooter, id=scooter_id)
        if not scooter.is_available:
            return render(request, 'error.html', {'msg': '该滑板车不可预订！'})
        
        if hire_period < scooter.min_hire_hours:
            return render(request, 'error.html', {
                'msg': f'最低起租 {scooter.min_hire_hours} 小时'
            })

        total_price = scooter.price_per_hour * hire_period

        new_order = Order.objects.create(
            guest_name=guest_name,
            guest_email=guest_email,
            user=None,
            scooter=scooter,
            hire_period=hire_period,
            total_price=total_price
        )
        
        scooter.is_available = False
        scooter.save()

        Thread(target=send_guest_booking_email, args=(new_order,)).start()

        return redirect("index") 

    scooters = Scooter.objects.filter(is_available=True).order_by('name')
    return render(request, "staff/staff_booking.html", {
        "scooters": scooters
    })

@login_required
def extend_booking(request, order_id):
    order = get_object_or_404(
        Order,
        id=order_id,
        user=request.user,
        pay_status='unpaid'
    )

    if request.method == 'POST':
        extra_hours = request.POST.get('extra_hours')

        if not extra_hours:
            return render(request, 'error.html', {'msg': '请输入延长小时数'})

        try:
            extra_hours = int(extra_hours)
        except:
            return render(request, 'error.html', {'msg': '小时数必须是数字'})

        if extra_hours <= 0:
            return render(request, 'error.html', {'msg': '延长时间必须大于0'})

        scooter = order.scooter
        extra_price = scooter.price_per_hour * extra_hours

        order.hire_period += extra_hours
        order.total_price += extra_price
        order.save()

        return redirect('my_orders')

    return render(request, 'order/extend.html', {
        'order': order
    })

@login_required
def feedback_create(request):
    if request.method == 'POST':
        scooter_id = request.POST.get('scooter_id')
        content = request.POST.get('content', '').strip()

        if not scooter_id:
            return render(request, 'error.html', {'msg': '请选择车辆'})
        if not content:
            return render(request, 'error.html', {'msg': '请填写问题描述'})

        scooter = get_object_or_404(Scooter, id=scooter_id)

        Feedback.objects.create(
            user=request.user,
            scooter=scooter,
            content=content
        )
        return render(request, 'feedback/success.html', {'msg': '反馈提交成功！'})

    scooters = Scooter.objects.all().order_by('name')
    return render(request, 'feedback/create.html', {'scooters': scooters})

@login_required
def my_feedback(request):
    feedbacks = Feedback.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'feedback/my_feedback.html', {'feedbacks': feedbacks})