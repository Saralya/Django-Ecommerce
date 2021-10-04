from django import template
from App_Order.models import Order

register = template.Library()

# this is a custom filter for counting

@register.filter
def cart_total(user):
    order = Order.objects.filter(user=user, ordered=False)

    if order.exists():
        return order[0].orderitems.count()  # cart e total koto gula item add kora hoise seta return korbe
    else:
        return 0