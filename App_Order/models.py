from django.db import models
from django.conf import settings

# Model
from App_Shop.models import Product
# Create your models here.


# ei model ta cart e ki ki item add kora hoise setar jonno
class Cart(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="cart")
    item = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    purchased = models.BooleanField(default=False)  # cart e kon item gula show korbo seta decide korbe (jegula akhno payment kora hoy nai)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.quantity} X {self.item}'

    # ei function ta individual item er total price ber korbe quantity hisebe
    def get_total(self):
        total = self.item.price * self.quantity
        float_total = format(total, '0.2f')
        return float_total


# ei model ta lagbe payment korar somoy
class Order(models.Model):
    orderitems = models.ManyToManyField(Cart)  # cart er sob gula item mile hobe 1ta order
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    ordered = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    paymentId = models.CharField(max_length=264, blank=True, null=True)
    orderId = models.CharField(max_length=200, blank=True, null=True)

    # ei function ta 1ta order er under e joto gula item ache tader total price dekhabe
    def get_totals(self):
        total = 0
        for order_item in self.orderitems.all():
            total += float(order_item.get_total())
        return total



# item 1(an object of Cart model)   400 * 3 = 1200  (using get_total())
# item 2(an object of Cart model)   200 * 4 = 800  (using get_total())

# orderitems 1(an object of Order model)   1200 + 800 = 2000  (using get_totals())

