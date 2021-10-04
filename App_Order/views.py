from django.shortcuts import render, get_object_or_404, redirect

# Authentications
from django.contrib.auth.decorators import login_required

# Model
from App_Order.models import Cart, Order
from App_Shop.models import Product
# Messages
from django.contrib import messages
# Create your views here.

@login_required
def add_to_cart(request, pk):
    item = get_object_or_404(Product, pk=pk)
    print("Item")
    print(item)
    order_item = Cart.objects.get_or_create(item=item, user=request.user, purchased=False) # item ta cart e add kora ache kina check korbe..thakle get korbe, na thakle create kore nibe
    print("Order Item Object:")
    print(order_item) # order_item akta tuple hisebe value return korbe jeta diye model er attributes access kora jay na
    print(order_item[0]) # sejnno order_item[0] indexing kore etake dictionary te convert kore nite hobe
    order_qs = Order.objects.filter(user=request.user, ordered=False) # ordered=False means incomplete order..cart er item gula oi order er under e jabe
    # order_qs e always 1ta object (incomplete order) e jabe karon user at a time 1ta order e korte parbe until this order is completed
    print("Order Qs:")
    print(order_qs) # prothom bar empty dekhabe karon kono existing order nei..tai else e dhuke akta new order create korbe
    
    # 2nd bar theke if condition e dhukbe
    if order_qs.exists():
        order = order_qs[0]
        print("If Order exist")
        print(order)
        if order.orderitems.filter(item=item).exists():
            order_item[0].quantity += 1 # already cart e add kora item jodi abar add kora hoy tahole notun kore add na kore ager tar quantity 1 barabe
            order_item[0].save()
            messages.info(request, "This item quantity was updated.")
            return redirect("App_Shop:home")
        else:
            order.orderitems.add(order_item[0]) # akta new item cart e add kora
            messages.info(request, "This item was added to your cart.")
            return redirect("App_Shop:home")
    
    else:
        # jodi ager kono order na thake tahole akta new order create korbo
        order = Order(user=request.user)
        order.save()
        order.orderitems.add(order_item[0])
        messages.info(request, "This item was added to your cart.")
        return redirect("App_Shop:home")


@login_required
def cart_view(request):
    carts = Cart.objects.filter(user=request.user, purchased=False)
    orders = Order.objects.filter(user=request.user, ordered=False)
    if carts.exists() and orders.exists():
        order = orders[0]
        return render(request, 'App_Order/cart.html', context={'carts':carts, 'order':order})
    else:
        messages.warning(request, "You don't have any item in your cart!")
        return redirect("App_Shop:home")


@login_required
def remove_from_cart(request, pk):
    item = get_object_or_404(Product, pk=pk)
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        if order.orderitems.filter(item=item).exists():
            order_item = Cart.objects.filter(item=item, user=request.user, purchased=False)[0]
            order.orderitems.remove(order_item) # Order model theke remove holo
            order_item.delete() # Cart model theke delete holo
            messages.warning(request, "This item was removed form your cart")
            return redirect("App_Order:cart")
        else:
            messages.info(request, "This item was not in your cart.")
            return redirect("App_Shop:home")
    else:
        messages.info(request, "You don't have an active order")
        return redirect("App_Shop:home")

@login_required
def increase_cart(request, pk):
    item = get_object_or_404(Product, pk=pk)
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        if order.orderitems.filter(item=item).exists():
            order_item = Cart.objects.filter(item=item, user=request.user, purchased=False)[0]
            if order_item.quantity >= 1:
                order_item.quantity += 1
                order_item.save()
                messages.info(request, f"{item.name} quantity has been updated")
                return redirect("App_Order:cart")
        else:
            messages.info(request, f"{item.name} is not in your cart")
            return redirect("App_Shop:home")
    else:
        messages.info(request, "You don't have an active order")
        return redirect("App_Shop:home")


@login_required
def decrease_cart(request, pk):
    item = get_object_or_404(Product, pk=pk)
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        if order.orderitems.filter(item=item).exists():
            order_item = Cart.objects.filter(item=item, user=request.user, purchased=False)[0]
            if order_item.quantity > 1:
                order_item.quantity -= 1
                order_item.save()
                messages.info(request, f"{item.name} quantity has been updated")
                return redirect("App_Order:cart")
            else:
                order.orderitems.remove(order_item)
                order_item.delete()
                messages.warning(request, f"{item.name} item has been removed from your cart")
                return redirect("App_Order:cart")
        else:
            messages.info(request, f"{item.name} is not in your cart")
            return redirect("App_Shop:home")
    else:
        messages.info(request, "You don't have an active order")
        return redirect("App_Shop:home")
