from django.shortcuts import render, redirect
import datetime
import razorpay
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.http import HttpResponse, JsonResponse

# import from apps
from carts import utils
from carts.models import CartItem
from .forms import OrderForm
from .models import Order, Payment, OrderProduct, UserCoupon
from fishWharf import settings
from accounts.models import Address, Account
from products.models import Product
import fishWharf.settings

client = razorpay.Client(auth=(settings.RAZOR_KEY_ID, settings.RAZOR_KEY_SECRET))



def coupon(request):
  if request.method == 'POST':
    coupon_code = request.POST['coupon']
    grand_total = request.POST['grand_total']
    coupon_discount = 0
    try:
      instance = UserCoupon.objects.get(user = request.user ,coupon__code = coupon_code)

      if float(grand_total) >= float(instance.coupon.min_value):
        coupon_discount = ((float(grand_total) * float(instance.coupon.discount))/100)
        grand_total = float(grand_total) - coupon_discount
        grand_total = format(grand_total, '.2f')
        coupon_discount = format(coupon_discount, '.2f')
        msg = 'Coupon Applied successfully'
        instance.used = True
        instance.save()
      else:
          msg='This coupon is only applicable for orders more than ₹'+ str(instance.coupon.min_value)+ '\- only!'
    except:
            msg = 'Coupon is not valid'
    response = {
               'grand_total': grand_total,
               'msg':msg,
               'coupon_discount':coupon_discount,
               'coupon_code':coupon_code,
                }

  return JsonResponse(response)

# ============================================================================== C O U P O N =============================================================================

@csrf_exempt
def payment_callback(request):
    if request.method == 'POST':
        payment_id = request.POST.get('razorpay_payment_id')
        order_id= request.POST.get('razorpay_order_id')
        client = razorpay.Client(auth=(fishWharf.settings.RAZOR_KEY_ID, fishWharf.settings.RAZOR_KEY_SECRET))
        payment = client.payment.fetch(payment_id)
        amount = payment['amount']
        status = payment['status']

        
        print(order_id,'=============================================================================================================   order id')

        if status == 'captured':
            #saving this payment details
            payment = Payment(
                user = request.user,
                payment_method = 'RazorPay',
                order_id = order_id,
                payment_id = payment_id,
                amount_paid = amount,
                status = status,
            )
            payment.save()
            
            #updating order table
            order_number = request.session.get('order_number', None)
            order = Order.objects.get(user = request.user , order_number = order_number)

            order.payment = payment
            order.is_ordered = True
            order.save()

            #assigning ordered cart items to order product table
            cart_items = CartItem.objects.filter(user = request.user)
            for item in cart_items:
                orderProduct = OrderProduct()
                orderProduct.order_id = order.id
                orderProduct.payment = payment
                orderProduct.user = request.user
                orderProduct.product_id = item.product_id
                orderProduct.quantity = item.quantity
                orderProduct.product_price = item.product.price
                orderProduct.ordered = True
                orderProduct.save()

                # Reducing the quantity of items from Stock in warehouse
                product = Product.objects.get(id = item.product_id)
                product.stock -= item.quantity
                product.save()

            order = Order.objects.get(order_number = order_number)
            ordered_products = OrderProduct.objects.filter(order_id = order.id)
            total = utils.total(ordered_products)
            tax = utils.tax(total)
            grand_total = utils.grand_total(total, tax)

            context = {
                'order_number': order_number,
                'order': order,
                'cart_items': ordered_products,
                'grand_total' : grand_total,
                'order' : order,
            }

             # Clearing the cart
            CartItem.objects.filter(user=request.user).delete()
        else:
            pass
        return render(request, 'orderSuccess.html', context)
    else:
        # Return an HTTP response with a bad request status code
        return HttpResponse(status=400)
    
# ======================================================================= C A L L  B A C K ==================================================================================

@login_required(login_url='login')
def place_order(request, total=0, quantity=0):
    current_user = request.user

    # If the cart count is less than or equal to 0, then redirect back to shop
    cart_items = CartItem.objects.filter(user = current_user)
    cart_count = cart_items.count()
    if cart_count <= 0:
       return redirect('shop')
    
    grand_total = 0
    tax = 0
    for cart_item in cart_items:
        total += (cart_item.product.price * cart_item.quantity)
        quantity += cart_item.quantity
    tax = utils.tax(total)
    grand_total = utils.grand_total(total, tax)

    razorpay_amount = grand_total * 100
    
   
              
    if request.method == 'POST':
        id = request.POST['flexRadioDefault']
        address  = Address.objects.get(pk = id)
        # user = current_user
        data = Order()
        data.user = current_user
        data.first_name = address.user.first_name
        data.last_name = address.user.last_name
        data.email = address.user.email
        data.phone = address.user.phone_number
        data.address_line_1 = address.address_line_1
        data.address_line_2 = address.address_line_2
        data.state = address.state
        data.city = address.city
        data.country = address.country
        
        data.order_total = grand_total
        data.tax = tax
        data.ip = request.META.get('REMOTE_ADDR')
    
        data.save()

        #generate order number 
        yr = int(datetime.date.today().strftime('%Y'))
        dt = int(datetime.date.today().strftime('%d'))
        mt = int(datetime.date.today().strftime('%m'))
        d = datetime.date(yr, mt, dt)
        current_date = d.strftime("%Y%m%d") #so the id will be like = 20040228
        order_number = current_date + str(data.id)
        data.order_number = order_number

        request.session['order_number'] = data.order_number
        request.session['grand_total'] = grand_total

        data.save()

        order = Order.objects.get(user=current_user, is_ordered=False, order_number = order_number)

        client = razorpay.Client(auth=(fishWharf.settings.RAZOR_KEY_ID, fishWharf.settings.RAZOR_KEY_SECRET))                         # razorpay fund collecting     -------------------------------------------
        payment = client.order.create({'amount':razorpay_amount , 'currency': 'INR', 'payment_capture': 1 })

        order_id = payment['id']
        
        
        context = {
            'order' : order,
            'cart_items' : cart_items,
            'total' : total,
            'tax' : tax,
            'grand_total' : grand_total,
            'payment' : payment,
            'order_id' : order_id,
        }

        return render(request, 'payments.html', context)
            
            # messages.error(request, 'Cannnot procceed until add new address')
    else:
        return redirect('checkout')

# ================================================================== P L A C E   O R D E R =================================================================================

def orderDetails(request, order_id):
    order = Order.objects.get(id = order_id)
    orderProduct = OrderProduct.objects.filter(order_id = order)
    # orderId = order.payment
    # payment = Payment.objects.get(order_id=order_id)

    context = {
        'order' : order,
        'orderProduct' : orderProduct,
        # 'payment:': payment,
    }
    return render(request, 'orderDetails.html', context)

# ===========================================================================================================================================================================

@login_required(login_url='login')
def cod(request):
    cart_items = CartItem.objects.filter(user = request.user)
    total = utils.total(cart_items) or 0
    quantity = utils.quantity(cart_items)
    tax = utils.tax(total)
    grand_total = utils.grand_total(total, tax)

    # saving payment
    payment = Payment(
        user = request.user,
        payment_method = 'COD',
        amount_paid = grand_total,
        status = 'captured',
    )
    payment.save()
    
    # updating order table
    order_number = request.session.get('order_number', None)
    order = Order.objects.get(user=request.user, order_number = order_number)

    order.payment = payment

    order.is_ordered = True
    order.save()

    # Moving Cart items in Order Table
    cart_items = CartItem.objects.filter(user = request.user)
    for item in cart_items:
        orderProduct = OrderProduct()
        orderProduct.order_id = order.id
        orderProduct.payment = payment
        orderProduct.user = request.user
        orderProduct.product_id = item.product_id
        orderProduct.quantity = item.quantity
        orderProduct.product_price = item.product.price
        orderProduct.ordered = True
        orderProduct.save()

        # Reducing the quantity of items from Stock in warehouse
        product = Product.objects.get(id = item.product_id)
        product.stock -= item.quantity
        product.save()

    order = Order.objects.get(order_number = order_number)
    ordered_products = OrderProduct.objects.filter(order_id = order.id)
    total = utils.total(ordered_products)
    tax = utils.tax(total)
    grand_total = utils.grand_total(total, tax)

    context = {
        'order_number': order_number,
        'order': order,
        'cart_items': ordered_products,
        'grand_total' : grand_total,
        'payment' : payment,
        
    }

    # Clearing the cart
    CartItem.objects.filter(user= request.user).delete()

    return render(request, 'orderSuccess.html', context)
# ================================================================================ C O D ===================================================================================

# @csrf_exempt
# def razorpay_payment(request):
#     grand_total = request.session.get('grand_total', None)
#     if request.method == 'POST':
#         amount = grand_total * 100     # multiplying with 100 because razorpay accepts amount in paisa instead of rupees
#         client = client.order.create(auth=(fishWharf.settings.RAZOR_KEY_ID, fishWharf.settings.RAZOR_KEY_SECRET))
#         payment = client.order.create({'amount': amount, 'currency': 'INR', 'payment_capture': '1'})

#         context = {
#             'payment' : payment
#         }
#         return render(request, 'payments.html', context)
#     return redirect('cart')

# =========================================================================== R A Z O R  P A Y =============================================================================

# def cancel_order(request, order_id):
#     order = Order.objects.get(id = order_id ,user = request.user)
#     order.status = "Cancelled"
#     order.save()
#     payment = Payment.objects.get(order_id = order_id)
#     payment.delete()
#     return redirect('orders')

client = razorpay.Client(auth=(settings.RAZOR_KEY_ID,settings.RAZOR_KEY_SECRET))
def cancel_order(request, paymentId):
    print(paymentId,'------------------------------------------------------order_id')
    payment = Payment.objects.get(id= paymentId, user=request.user)
    payment_id = payment.payment_id
    refund_amount = payment.amount_paid
    payment_method = payment.payment_method
    order_number = payment.order_id
    order = Order.objects.get(payment_id = paymentId)
    print(payment_id,refund_amount,payment_method,order_number,'-------------------------payment----------------------------')

    if payment_method == 'RazorPay':
        try:
            client.payment.refund(payment_id,{
                "amount" : refund_amount,
                "speed" : "optimum",
                "receipt": order_number,
            })
            payment.status = 'Cancelled'
            order.status = 'Cancelled'
            order.save()
            payment.save()
            messages.success(request, 'Payment initiated successfuly!')
            return redirect('orders')
        except Exception as e:
            messages.error(request, 'Failed to initiate refund: ' + str(e))
            return redirect('home')

# ============================================================================== R E T U R N =============================================================================