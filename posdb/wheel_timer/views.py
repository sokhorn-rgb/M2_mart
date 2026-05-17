# sales/views.py

from django.shortcuts import render, get_object_or_404
from .models import Product, Order


def product_list(request):
    """បង្ហាញផលិតផល active ទាំងអស់ តម្រៀប A–Z"""
    products = Product.objects.filter(is_active=True)
    return render(request, 'sales/product_list.html', {'products': products})


def product_detail(request, pk):
    """បង្ហាញព័ត៌មានលម្អិតសម្រាប់ផលិតផលតែមួយ។ Return 404 ប្រសិនបើរកមិនឃើញ"""
    product = get_object_or_404(Product, pk=pk)
    return render(request, 'sales/product_detail.html', {'product': product})


def order_list(request):
    """បង្ហាញការបញ្ជាទិញទាំងអស់ ថ្មីបំផុតមុន"""
    orders = Order.objects.all()
    return render(request, 'sales/order_list.html', {'orders': orders})