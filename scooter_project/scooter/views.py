import datetime
import json
from decimal import Decimal
from functools import wraps
from threading import Thread

from django import forms
from django.conf import settings
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models import Sum
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone, translation
from django.utils.translation import gettext as _
from django.utils.translation import gettext_lazy as _lazy

from .models import Card, Feedback, Order, Scooter


MEMBERSHIP_GROUPS = ("Student", "Elderly", "FrequentUser")
DISCOUNT_PRIORITY = ("FrequentUser", "Elderly", "Student")
DISCOUNT_RATES = {
    "FrequentUser": Decimal("0.80"),
    "Elderly": Decimal("0.85"),
    "Student": Decimal("0.90"),
}
MONEY_QUANTIZE = Decimal("0.01")
HIGH_PRIORITY_KEYWORDS = (
    '坏', '故障', '不能用', '动不了', '碎',
    '爆胎', '危险', '失灵', '报错', '无法',
    '用不了', '没反应', '失控', '异常'
)
FEEDBACK_PRIORITIES = {choice[0] for choice in Feedback.PRIORITY_CHOICES}
FEEDBACK_STATUSES = {choice[0] for choice in Feedback.STATUS_CHOICES}


def admin_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_superuser:
            return render(request, 'error.html', {'msg': _('无管理员权限')})
        return view_func(request, *args, **kwargs)
    return login_required(wrapper)


def staff_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_staff:
            return render(request, 'error.html', {'msg': _('无员工权限')})
        return view_func(request, *args, **kwargs)
    return login_required(wrapper)


def get_discount(user):
    if not user or not user.is_authenticated:
        return Decimal("1.00")
    
    user_groups = set(user.groups.values_list('name', flat=True))
    for group_name in DISCOUNT_PRIORITY:
        if group_name in user_groups:
            return DISCOUNT_RATES[group_name]
    
    return Decimal("1.00")


def get_membership_groups(user):
    if not user or not user.is_authenticated:
        return []

    user_groups = set(
        user.groups
        .filter(name__in=MEMBERSHIP_GROUPS)
        .values_list('name', flat=True)
    )
    return [group for group in MEMBERSHIP_GROUPS if group in user_groups]


def start_background_email(target, *args):
    Thread(target=target, args=args, daemon=True).start()


class RegisterForm(forms.ModelForm):
    username = forms.CharField(label=_lazy("用户名"))
    email = forms.EmailField(label=_lazy("邮箱"), required=True)
    password1 = forms.CharField(label=_lazy("密码"), widget=forms.PasswordInput)
    password2 = forms.CharField(label=_lazy("确认密码"), widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ["username", "email"]

    def clean_username(self):
        username = self.cleaned_data.get("username")
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError(_("用户名已存在"))
        return username

    def clean_password1(self):
        pwd = self.cleaned_data.get("password1")

        if len(pwd) < 8:
            raise forms.ValidationError(_("密码长度不能小于8位"))
        if not any(c.isalpha() for c in pwd):
            raise forms.ValidationError(_("密码必须包含字母"))
        if not any(c.isdigit() for c in pwd):
            raise forms.ValidationError(_("密码必须包含数字"))

        return pwd

    def clean_password2(self):
        pwd1 = self.cleaned_data.get("password1")
        pwd2 = self.cleaned_data.get("password2")
        if pwd1 and pwd2 != pwd1:
            raise forms.ValidationError(_("两次输入的密码不一致"))
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
    ongoing_orders = (
        Order.objects
        .filter(user=request.user, pay_status='unpaid')
        .select_related('scooter')
        .order_by('-order_time')[:3]
    )

    scooters_data = list(
        scooters.values('id', 'name', 'address', 'latitude', 'longitude')
    )

    return render(request, 'index.html', {
        'username': request.user.username,
        'membership_groups': get_membership_groups(request.user),
        'scooters': scooters,
        'ongoing_orders': ongoing_orders,
        'scooters_data': scooters_data
    })


@login_required
def create_order_page(request, scooter_id):
    scooter = get_object_or_404(Scooter, id=scooter_id)
    if not scooter.is_available:
        return render(request, 'error.html', {'msg': _('该滑板车不可预订！')})
    return render(request, 'order/create_order.html', {'scooter': scooter})


def send_confirmation_email(order, lang):
    with translation.override(lang):
        subject = _("滑板车预订确认")
        message = _(
            "你好 {username}：\n\n"
            "你已成功预订电动滑板车！\n"
            "订单编号：{order_id}\n"
            "滑板车编号：{scooter_name}\n"
            "租赁时长：{hire_period} 小时\n"
            "订单总价：¥{total_price}\n"
            "下单时间：{order_time}\n\n"
            "请尽快完成支付。"
        ).format(
            username=order.user.username,
            order_id=order.id,
            scooter_name=order.scooter.name,
            hire_period=order.hire_period,
            total_price=order.total_price,
            order_time=order.order_time.strftime('%Y-%m-%d %H:%M'),
        )
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
        return render(request, 'error.html', {'msg': _('该页面仅支持表单提交，请勿直接访问！')})

    scooter_id = request.POST.get('scooter_id')
    hire_period = request.POST.get('hire_period')

    if not scooter_id or not hire_period:
        return render(request, 'error.html', {'msg': _('请选择租赁时长！')})

    try:
        hire_period = int(hire_period)
    except (TypeError, ValueError):
        return render(request, 'error.html', {'msg': _('小时数必须是数字')})

    scooter = get_object_or_404(Scooter, id=scooter_id)
    if not scooter.is_available:
        return render(request, 'error.html', {'msg': _('该滑板车不可预订！')})

    if hire_period < scooter.min_hire_hours:
        return render(request, 'error.html', {
            'msg': _('最低起租 {hours} 小时').format(hours=scooter.min_hire_hours)
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

    # 记录当前语言，用于异步邮件
    current_lang = translation.get_language() or settings.LANGUAGE_CODE
    start_background_email(send_confirmation_email, new_order, current_lang)

    return render(request, 'order_success.html', {
        'order': new_order
    })


@login_required
def pay_order(request, order_id):
    try:
        order = Order.objects.get(id=order_id, user=request.user)
    except Order.DoesNotExist:
        return render(request, 'error.html', {'msg': _('订单不存在！')})

    if order.pay_status == 'paid':
        return render(request, 'error.html', {'msg': _('该订单已支付，无需重复支付！')})
    if order.pay_status == 'cancelled':
        return render(request, 'error.html', {'msg': _('该订单已取消，无法支付！')})

    origin_price = order.scooter.price_per_hour * order.hire_period
    discount = get_discount(request.user)
    order.total_price = (origin_price * discount).quantize(MONEY_QUANTIZE)

    if request.method == 'POST':
        order.pay_status = 'paid'
        order.save()
        return render(request, 'order/pay_success.html', {
            'order': order,
            'origin_price': origin_price
        })

    return render(request, 'order/pay_order.html', {
        'order': order,
        'origin_price': origin_price
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
        return render(request, 'error.html', {'msg': _('该页面仅支持表单提交，请勿直接访问！')})

    try:
        order = Order.objects.get(
            id=order_id,
            user=request.user,
            pay_status='unpaid'
        )
    except Order.DoesNotExist:
        return render(request, 'error.html', {'msg': _('无法取消该订单（订单不存在/已支付/已取消）！')})

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
    today = timezone.localdate()
    monday = today - datetime.timedelta(days=today.weekday())
    sunday = monday + datetime.timedelta(days=6)
    start_datetime = timezone.make_aware(
        datetime.datetime.combine(monday, datetime.time.min)
    )
    end_datetime = timezone.make_aware(
        datetime.datetime.combine(sunday, datetime.time.max)
    )

    standard_periods = [
        ('1h', _('1小时档'), 1, 4),
        ('4h', _('4小时档'), 4, 24),
        ('1d', _('1天档(24h)'), 24, 168),
        ('1w', _('1周档(168h)'), 168, 9999),
    ]

    paid_orders = Order.objects.filter(
        pay_status='paid',
        order_time__gte=start_datetime,
        order_time__lte=end_datetime
    )

    stat_data = []
    for period_key, period_name, min_h, max_h in standard_periods:
        period_orders = paid_orders.filter(
            hire_period__gte=min_h,
            hire_period__lt=max_h
        )

        order_count = period_orders.count()
        total_income = period_orders.aggregate(Sum('total_price'))['total_price__sum'] or 0.00
        total_income = round(float(total_income), 2)

        stat_data.append({
            'period': period_key,
            'period_name': period_name,
            'order_count': order_count,
            'total_income': total_income,
            'is_hot': False
        })

    max_order_count = max((item['order_count'] for item in stat_data), default=0)
    for item in stat_data:
        item['is_hot'] = item['order_count'] == max_order_count and max_order_count > 0

    total_weekly_income = sum(item['total_income'] for item in stat_data)
    total_weekly_income = round(total_weekly_income, 2)

    daily_income = []
    for i in range(7):
        day = monday + datetime.timedelta(days=i)
        day_start = timezone.make_aware(
            datetime.datetime.combine(day, datetime.time.min)
        )
        day_end = timezone.make_aware(
            datetime.datetime.combine(day, datetime.time.max)
        )
        day_orders = paid_orders.filter(order_time__gte=day_start, order_time__lte=day_end)
        day_total = day_orders.aggregate(Sum('total_price'))['total_price__sum'] or 0.00
        day_count = day_orders.count()
        daily_income.append({
            'date': day,
            'income': round(float(day_total), 2),
            'order_count': day_count
        })

    max_count = max((d['order_count'] for d in daily_income), default=0)
    for d in daily_income:
        d['is_popular'] = (d['order_count'] == max_count) and (max_count > 0)

    return render(request, 'admin/weekly_income.html', {
        'monday': monday.strftime('%Y-%m-%d'),
        'sunday': sunday.strftime('%Y-%m-%d'),
        'stat_data': stat_data,
        'total_weekly_income': round(total_weekly_income, 2),
        'has_data': total_weekly_income > 0,
        'daily_income': daily_income,
        'stat_json': json.dumps(stat_data, cls=DjangoJSONEncoder),
        'daily_json': json.dumps(daily_income, cls=DjangoJSONEncoder)
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
            return render(request, 'card/add.html', {'msg': _('卡号至少4位')})

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


def send_guest_booking_email(order, lang):
    with translation.override(lang):
        subject = _("滑板车预订确认（代下单）")
        message = _(
            "您好 {guest_name}：\n\n"
            "员工已为您代预订滑板车！\n"
            "订单编号：{order_id}\n"
            "滑板车编号：{scooter_name}\n"
            "租赁时长：{hire_period} 小时\n\n"
            "感谢使用！"
        ).format(
            guest_name=order.guest_name,
            order_id=order.id,
            scooter_name=order.scooter.name,
            hire_period=order.hire_period,
        )
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[order.guest_email],
            fail_silently=True,
        )


@login_required
@staff_required
def staff_create_booking(request):
    if request.method == "POST":
        guest_name = request.POST.get("guest_name")
        guest_email = request.POST.get("guest_email")
        scooter_id = request.POST.get('scooter_id')
        hire_period = request.POST.get('hire_period')

        if not scooter_id or not hire_period:
            return render(request, 'error.html', {'msg': _('请选择租赁时长！')})

        try:
            hire_period = int(hire_period)
        except (TypeError, ValueError):
            return render(request, 'error.html', {'msg': _('小时数必须是数字')})

        scooter = get_object_or_404(Scooter, id=scooter_id)
        if not scooter.is_available:
            return render(request, 'error.html', {'msg': _('该滑板车不可预订！')})

        if hire_period < scooter.min_hire_hours:
            return render(request, 'error.html', {
                'msg': _('最低起租 {hours} 小时').format(hours=scooter.min_hire_hours)
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

        current_lang = translation.get_language() or settings.LANGUAGE_CODE
        start_background_email(send_guest_booking_email, new_order, current_lang)

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
            return render(request, 'error.html', {'msg': _('请输入延长小时数')})

        try:
            extra_hours = int(extra_hours)
        except (TypeError, ValueError):
            return render(request, 'error.html', {'msg': _('小时数必须是数字')})

        if extra_hours <= 0:
            return render(request, 'error.html', {'msg': _('延长时间必须大于0')})

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
            return render(request, 'error.html', {'msg': _('请选择车辆')})
        if not content:
            return render(request, 'error.html', {'msg': _('请填写问题描述')})

        scooter = get_object_or_404(Scooter, id=scooter_id)

        priority = 'high' if any(word in content for word in HIGH_PRIORITY_KEYWORDS) else 'low'

        Feedback.objects.create(
            user=request.user,
            scooter=scooter,
            content=content,
            priority=priority
        )
        return render(request, 'feedback/success.html', {'msg': _('反馈提交成功！')})

    scooters = Scooter.objects.all().order_by('name')
    return render(request, 'feedback/create.html', {'scooters': scooters})


@login_required
def my_feedback(request):
    feedbacks = Feedback.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'feedback/my_feedback.html', {'feedbacks': feedbacks})


@login_required
@staff_required
def feedback_list(request):
    priority = request.GET.get('priority', '')
    status = request.GET.get('status', '')

    feedbacks = Feedback.objects.all()

    if priority in FEEDBACK_PRIORITIES:
        feedbacks = feedbacks.filter(priority=priority)

    if status in FEEDBACK_STATUSES:
        feedbacks = feedbacks.filter(status=status)

    feedbacks = feedbacks.order_by('-created_at')

    return render(request, 'feedback/list.html', {
        'feedbacks': feedbacks,
        'priority': priority,
        'status': status,
    })


@login_required
@staff_required
def feedback_update(request, feedback_id):
    feedback = get_object_or_404(Feedback, id=feedback_id)

    if request.method == 'POST':
        priority = request.POST.get('priority')
        status = request.POST.get('status')
        if priority not in FEEDBACK_PRIORITIES or status not in FEEDBACK_STATUSES:
            return render(request, 'error.html', {'msg': _('反馈状态或优先级无效')})

        feedback.priority = priority
        feedback.status = status
        feedback.save()

        return redirect('feedback_list')

    return render(request, 'feedback/edit.html', {'feedback': feedback})
