from django.urls import path

from . import views
from .views import * 

urlpatterns = [
    path('', views.adminLogin, name="adminLogin"),
    path('dashboard/' , AdminDashboard.as_view(), name="adminDashboard"),
    path('logout/', views.adminLogout, name="adminLogout"),


    path('users/', UsersList.as_view(), name="usersList"),
    path('user/edit/<int:user_id>/', views.userEdit, name="userEdit"),
    path('user/status/<int:user_id>/', views.userStatus, name="userStatus"),
    path('user-search/' , views.UserSearch, name = 'user_search'),


    path('products/', ProductsList.as_view(), name='productsList'),
    path('product-edit/<int:pk>', EditProduct.as_view(), name="editProduct"),
    path('product/create/', views.product_create, name="productCreate"),
    path('product/status/<int:product_id>/', views.productStatus, name="productStatus"),
    path('product-search/' , views.ProductSearch, name = 'product_search'),


    path('categories/', CategoryList.as_view(), name="categoryList"),
    path('category/create/', views.category_create, name="categoryCreate"),
    path('category-edit/<int:pk>', EditCategory.as_view(), name="editCategory"),
    path('category/status/<int:category_id>/', views.categoryStatus, name="categoryStatus"),
    path('category_search/' , views.category_search, name = 'category_search'),


    path('coupons/', CouponList.as_view(), name="couponList"),
    path('coupon/create/', views.coupon_create, name="couponCreate"),
    path('coupon-edit/<int:pk>', EditCoupon.as_view(), name="editCoupon"),
    path('coupon/status/<int:coupon_id>/', views.couponStatus, name="couponStatus"),
    path('coupons/search/' , views.coupon_search, name = 'coupon_search'),


    path('orders/', OrdersList.as_view(), name = "ordersList")
]