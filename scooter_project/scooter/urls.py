from django.urls import path, include
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('register/', views.register, name='register'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('order/create/<int:scooter_id>/', views.create_order_page, name='create_order_page'),
    path('order/submit/', views.submit_order, name='submit_order'),
    path('order/pay/<int:order_id>/', views.pay_order, name='pay_order'),
    path('order/my/', views.my_orders, name='my_orders'),
    path('order/cancel/<int:order_id>/', views.cancel_order, name='cancel_order'),
    path('income/weekly/', views.weekly_income, name='weekly_income'),
    path('card/list/', views.card_list, name='card_list'),
    path('card/add/', views.card_add, name='card_add'),
    path('card/delete/<int:card_id>/', views.card_delete, name='card_delete'), 
    path('card/set-default/<int:card_id>/', views.set_default_card, name='set_default_card'),
    path("staff/create-booking/", views.staff_create_booking, name="staff_create_booking"),
]