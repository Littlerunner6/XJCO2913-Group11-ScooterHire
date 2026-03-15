from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('order/create/<int:scooter_id>/', views.create_order_page, name='create_order_page'),
    path('order/submit/', views.submit_order, name='submit_order'),
    path('order/pay/<int:order_id>/', views.pay_order, name='pay_order'),
    path('order/my/', views.my_orders, name='my_orders'),
    path('order/cancel/<int:order_id>/', views.cancel_order, name='cancel_order'),
]