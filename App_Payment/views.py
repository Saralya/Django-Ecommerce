from django.shortcuts import render, HttpResponseRedirect, redirect
from django.urls import reverse
from django.contrib import messages
#models and forms
from App_Order.models import Order, Cart
from App_Payment.forms import BillingAddress
from App_Payment.forms import BillingForm


from django.contrib.auth.decorators import login_required

# for payment
import requests
from sslcommerz_python.payment import SSLCSession
from decimal import Decimal
import socket
from django.views.decorators.csrf import csrf_exempt

# Create your views here.
@login_required
def checkout(request):
    saved_address = BillingAddress.objects.get_or_create(user=request.user)
    saved_address = saved_address[0]
    print(saved_address)
    form = BillingForm(instance=saved_address)
    if request.method == "POST":
        form = BillingForm(request.POST, instance=saved_address)
        if form.is_valid():
            form.save()
            form = BillingForm(instance=saved_address)
            messages.success(request, f"Shipping Address Saved!")
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    #print(order_qs)
    order_items = order_qs[0].orderitems.all()
    #print(order_items)
    order_total = order_qs[0].get_totals()
    return render(request, 'App_Payment/checkout.html', context={"form":form, "order_items":order_items, "order_total":order_total, "saved_address":saved_address})

@login_required
def payment(request):
    saved_address = BillingAddress.objects.get_or_create(user=request.user)
    saved_address = saved_address[0]

    # ei 2ta validation lagbe for sslcommerz payment
    if not saved_address.is_fully_filled():
        messages.info(request, f"Please complete shipping address!")
        return redirect("App_Payment:checkout")

    if not request.user.profile.is_fully_filled():
        messages.info(request, f"Please complete profile details!")
        return redirect("App_Login:profile")


    # from sslcommerz docs
    store_id = 'abc615c114113ffa'
    API_key = 'abc615c114113ffa@ssl'
    mypayment = SSLCSession(sslc_is_sandbox=True, sslc_store_id=store_id, sslc_store_pass=API_key) # 1st parameter ta true karon eta practise..real payment e false dibo

    status_url = request.build_absolute_uri(reverse("App_Payment:complete")) # build_absolute_uri() function ta j view theke call kora hocche tar url show korbe, reverse use kore onno view te newa jay
    #print(status_url)
    mypayment.set_urls(success_url=status_url, fail_url=status_url, cancel_url=status_url, ipn_url=status_url) # payment success/fail/cancel/special notification egular jonno alada view na likhe akta view (complete) er moddhei sob niye ashbo

    # order tar sob info set_product_integration() e dicchi
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    order_items = order_qs[0].orderitems.all()
    order_items_count = order_qs[0].orderitems.count()
    order_total = order_qs[0].get_totals()

    mypayment.set_product_integration(total_amount=Decimal(order_total), currency='BDT', product_category='Mixed', product_name=order_items, num_of_item=order_items_count, shipping_method='Courier', product_profile='None')

    # user tar sob info set_customer_info() e dicchi
    current_user = request.user
    mypayment.set_customer_info(name=current_user.profile.full_name, email=current_user.email, address1=current_user.profile.address_1, address2=current_user.profile.address_1, city=current_user.profile.city, postcode=current_user.profile.zipcode, country=current_user.profile.country, phone=current_user.profile.phone)

    # billing address tar sob info set_shipping_info() e dicchi
    mypayment.set_shipping_info(shipping_to=current_user.profile.full_name, address=saved_address.address, city=saved_address.city, postcode=saved_address.zipcode, country=saved_address.country)

    response_data = mypayment.init_payment()
    #print(response_data)
    return redirect(response_data['GatewayPageURL']) # response_data te sslcommerz er akta url ache sekhane redirect korte hobe..ekhane payment initialize hoy
    # kono data template e collect korte . use kori, but dictionary ba Json data collect korte hoy key dhore. eg: ['GatewayPageURL']


@csrf_exempt  # eta dile csrf verification check korbe na...jehetu sslcommerz theke completion info gula POST hisebe pathay tai django csrf verification chabe..etake off korte hobe
def complete(request):
    if request.method == 'POST' or request.method == 'post':
        payment_data = request.POST
        status = payment_data['status']

        # status, val_id, tran_id egula sob holo sslcommerz theke pathano json datar key
        if status == 'VALID':
            val_id = payment_data['val_id']
            tran_id = payment_data['tran_id']
            messages.success(request,f"Your Payment Completed Successfully! Page will be redirected!")
            return HttpResponseRedirect(reverse("App_Payment:purchase", kwargs={'val_id':val_id, 'tran_id':tran_id},))
            # payment successful howar por purchase page e tran_id, val_id gula kwargs hisebe pathacchi jate egula model e save kora jay
        elif status == 'FAILED':
            messages.warning(request, f"Your Payment Failed! Please Try Again! Page will be redirected!")

    return render(request, "App_Payment/complete.html", context={})

@login_required
def purchase(request, val_id, tran_id):
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    order = order_qs[0]
    
    order.ordered = True  # model e ordered=False chilo..etake akhn True korte hobe, na hole payment completion er por o cart e theke jabe
    order.orderId = tran_id
    order.paymentId = val_id
    order.save()
    cart_items = Cart.objects.filter(user=request.user, purchased=False)
    for item in cart_items:
        item.purchased = True # same here
        item.save()
    return HttpResponseRedirect(reverse("App_Shop:home"))

@login_required
def order_view(request):
    try:
        orders = Order.objects.filter(user=request.user, ordered=True)
        context = {"orders": orders}
    except:
        messages.warning(request, "You do no have an active order")
        return redirect("App_Shop:home")
    return render(request, "App_Payment/order.html", context)
