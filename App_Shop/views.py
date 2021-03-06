
from django.shortcuts import render

# Import views
from django.views.generic import ListView, DetailView

# Models
from App_Shop.models import Product

# Mixin
from django.contrib.auth.mixins import LoginRequiredMixin  # same as @login_required
# Create your views here.



class Home(ListView):
    model = Product
    template_name = 'App_Shop/home.html'

class ProductDetail(DetailView):  # use LoginRequiredMixin here if needed
    model = Product
    template_name = 'App_Shop/product_detail.html'
