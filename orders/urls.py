from django.urls import path
from . import views

urlpatterns = [
    path('place_order/', views.place_order, name='place_order'),
    path('cash-on-delivery/', views.cod, name='cod'),
    path('whatsapp-redirect/', views.whatsapp_redirect, name='whatsapp_redirect'),
    
    # path('razorpay-payment/', views.razorpay_payment, name='razorpay_payment'),
    path('payment-callback', views.payment_callback, name="payment_callback"),

    path('order-details/<int:order_id>/', views.orderDetails, name = 'orderDetails'),
    path("coupon/", views.coupon, name='coupon'),

    path('cancel-order/<int:paymentId>/', views.cancel_order, name="cancel_order"),
]