from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.generic import TemplateView, ListView
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.views.generic.edit import UpdateView, CreateView
from django.db.models import Q
from django.db.models import Sum

from accounts.models import Account
from accounts.forms import UserForm
from category.forms import CategoryForm
from products.models import Product
from orders.models import Coupon, Order, Payment
from orders.forms import CouponForm
from category.models import Category
from products.forms import ProductForm


# Create your views here.

def adminLogin(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']

        user = authenticate(email = email, password = password)

        if user is not None:
            login(request, user)
            return redirect('adminDashboard')
        else:
            messages.error(request, 'Access Denied !')
    return render(request, 'adminLogin.html')

def adminLogout(request):
    logout(request)
    request.session.flush()
    return redirect('adminLogin')


class AdminDashboard(UserPassesTestMixin, LoginRequiredMixin, TemplateView ):
    template_name = 'adminDashboard.html'
    login_url = reverse_lazy('adminLogin')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user_count'] = Account.objects.all().count()
        context['product_count'] = Product.objects.all().count()
        context['order_count'] = Order.objects.all().count()
        context['total_amount'] = Payment.objects.aggregate(Sum('amount_paid'))['amount_paid__sum']/100


        return context
    
    def test_func(self):
        return self.request.user.is_admin
    
    def handle_no_permission(self):
        if self.request.user.is_authenticated:
            messages.error(self.request , 'You don\'t have permission to access this page.')
            return redirect('adminLogin')
        

# ====================================================================== U S E R  M A N A G M E N T ==========================================================================

class UsersList(UserPassesTestMixin, LoginRequiredMixin, ListView):
    login_url = reverse_lazy('adminLogin')
    template_name = 'usersList.html'
    model = Account
    context_object_name = 'users'
    paginate_by = 7

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # context['users'] = Account.objects.all()
        context['user_count'] = Account.objects.all().count()
        return context
    
    def test_func(self):
        return self.request.user.is_admin
    
    def handle_no_permission(self):
        if self.request.user.is_authenticated:
            messages.error(self.request , 'You don\'t have permission to access this page.')
            return redirect('adminLogin')
    
@login_required(login_url='adminLogin')
@user_passes_test(lambda u: u.is_admin)
def userEdit(request, user_id):
    try:
        user = Account.objects.get(id = user_id)
    except Account.DoesNotExist:
        pass
    
    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=user)
        if user_form.is_valid():
            user_form.save()
            return redirect('usersList')
    else:
        user_form = UserForm(instance=user)
        
    context = {
        'user' : user_form,
        'user_id': user.id
    }   
    
    return render(request, 'userEdit.html', context)


def userStatus(request, user_id):
    user = Account.objects.get(id = user_id)
    if user.is_active:
        user.is_active = False
    else:
        user.is_active = True
    user.save()
    return redirect('usersList')

def UserSearch(request):
    if 'keyword' in request.GET:
        keyword = request.GET.get('keyword')
        users = Account.objects.filter(Q(first_name__icontains = keyword) | Q(last_name__icontains = keyword)  | Q(email__icontains = keyword) | Q(phone_number__icontains = keyword))
    return render(request, 'usersList.html', {'users':users})


# ====================================================================== P R O D U C T   M A N A G M E N T ==========================================================================


class ProductsList(LoginRequiredMixin, ListView):
    login_url = reverse_lazy('adminLogin')
    template_name = 'productsList.html'
    model =  Product
    ordering = ['-modified_date']
    context_object_name = 'products'
    paginate_by = 5
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["product_count"] = Product.objects.all().count()
        context["product_available"] = Product.objects.filter(is_available = True).count()
        return context
    

    
def product_create(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Product added successfully!')
            return redirect('productsList')
    else:
        form = ProductForm()
    context = {
        'form' : form
    }

    return render(request, 'productCreate.html', context)

    
# Edit Product
class EditProduct(LoginRequiredMixin, UpdateView):
    login_url =reverse_lazy('adminLogin')
    model = Product
    form_class = ProductForm
    template_name = 'productEdit.html'
    success_url = reverse_lazy('productsList')
    

def productStatus(request, product_id):
    product = Product.objects.get(id = product_id)
    if product.is_available:
        product.is_available = False
    else:
        product.is_available = True
    product.save()
    return redirect('productsList')

def ProductSearch(request):
    if 'keyword' in request.GET:
        keyword = request.GET.get('keyword')
        products = Product.objects.order_by('created_date').filter(Q(description__icontains = keyword) | Q(product_name__icontains = keyword))
    return render(request, 'productsList.html', {'products':products})


# ====================================================================== C A T E G O R Y   M A N A G M E N T ==========================================================================


class CategoryList(LoginRequiredMixin, ListView):
    template_name = 'categoryList.html'
    model = Category
    context_object_name = 'category'
    ordering = ['-id']
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["category_count"] = Category.objects.all().count()
        return context
    


def category_create(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('categoryList')
    else:
        form = CategoryForm()
    context = {
        'form' : form,
    }
    return render(request, 'categoryCreate.html', context)

class EditCategory(LoginRequiredMixin, UpdateView):
    login_url = reverse_lazy('adminLogin')
    model = Category
    form_class = CategoryForm
    template_name = 'categoryEdit.html'
    success_url = reverse_lazy('categoryList')

def categoryStatus(request, category_id):
    category = Category.objects.get(id = category_id)
    if category.is_available:
        category.is_available = False
    else:
        category.is_available = True
    category.save()
    return redirect('categoryList')

def category_search(request):
    if 'keyword' in request.GET:
        keyword = request.GET.get('keyword')
        category = Category.objects.order_by('id').filter(Q(description__icontains = keyword) | Q(category_name__icontains = keyword))
    return render(request, 'categoryList.html', {'category':category})





# ====================================================================== C O U P O N   M A N A G M E N T ==========================================================================


class CouponList(LoginRequiredMixin, ListView):
    login_url = reverse_lazy('adminLogin')
    template_name = 'couponList.html'
    model = Coupon
    context_object_name = 'coupons'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["coupons_count"] = Coupon.objects.all().count()
        return context


def coupon_create(request):
    if request.method == 'POST':
        form = CouponForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Coupen added successfully!')
            return redirect('couponList')
    else:
        form = CouponForm()
    context = {
        'form' : form
    }

    return render(request, 'couponCreate.html', context)

class EditCoupon(LoginRequiredMixin, UpdateView):
    login_url = reverse_lazy('adminLogin')
    template_name = 'couponEdit.html'
    model = Coupon
    form_class = CouponForm
    success_url = reverse_lazy('couponList')
    

def couponStatus(request, coupon_id):
    coupon = Coupon.objects.get(id = coupon_id)
    if coupon.active == True:
        coupon.active = False
    else:
        coupon.active = True
    coupon.save()
    return redirect('couponList')

def coupon_search(request):
    if 'keyword' in request.GET:
        keyword = request.GET.get('keyword')
        coupon = Coupon.objects.order_by('id').filter(Q(code__icontains = keyword) | Q(discount__icontains = keyword))
    return render(request, 'couponList.html', {'coupon':coupon}) 




# ====================================================================== C O U P O N   M A N A G M E N T ==========================================================================



class OrdersList(LoginRequiredMixin, ListView):
    login_url = reverse_lazy('adminLogin')
    template_name = 'ordersList.html'
    model = Order
    context_object_name = 'orders'
    ordering = ['-created_at']
    paginate_by = 15

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["orders_count"] = Order.objects.all().count()
        return context
    
    
        

def order_status(request, order_id):
    order = Order.objects.get(id = order_id)

    if request.method == "POST":
        status = request.POST.get('status')
        if status == 'Delivered':
            if order.status == 'Cancelled':
                messages.error(request, 'This order has already been delivered and cannot be cancelled.')
            else:
                order.status = 'Delivered'
                order.save()
                messages.success(request, f'Order with tracking id {order.order_number} has been Delivered.')
        elif status == 'Cancelled':
            if order.status == 'Delivered':
                messages.error(request, 'This order has already been delivered and cannot be cancelled.')
            else:
                order.status = 'Cancelled'
                order.save()
                messages.success(request, f'Order with tracking id {order.order_number} has been Cancelled.')
        elif status == 'Refunded':
            if order.payment.payment_method == 'RazorPay':
                if order.status == 'Cancelled':
                    order.status = 'Refunded'
                    order.save()
                    messages.success(request, 'Order Refunded !')
                else:
                    messages.error(request, 'This action can\'t be done since this product is not Cancelled !')
            else:
                messages.error(request, 'Cash on Delivery Orders cant be refunded!')

    context ={
        'order' : order,
    }

    return render(request, 'orderStatus.html', context)

# def sales_data(request):
#     if request.method == 'POST':
#          start_date = request.POST['start_date']
#          end_date = request.POST['end_date']
#          order = Payment.objects.filter(created_at__range=[start_date, end_date])
         
#          try:
#             total_amount_paid = order.aggregate(Sum('amount_paid'))['amount_paid__sum']
#          except Exception as e:
#             raise e 
         
#          context = {
#              'order' : order,
#              'total_amount_paid' : total_amount_paid,
#          }
#          return render(request, 'sales_report.html', context)
#     return render(request, 'sales_report.html')
    