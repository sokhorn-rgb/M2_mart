# sales/views.py

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Product, Order, OrderItem
from .forms import OrderItemForm
from django.db.models import Sum
from django.utils import timezone
from django.db import transaction
# views.py

def cancel_order(request, pk):
    order = get_object_or_404(Order, pk=pk)
    
    with transaction.atomic():
        # ១. បូកស្តុកត្រឡប់មកវិញ (Code ចាស់របស់អ្នក)
        for item in order.items.all():
            product = item.product
            # ប្រើ product.stock ឬ product.quantity តាមដែលអ្នកបានកែរួច
            product.stock += item.quantity 
            product.save()

        # ២. លុប Order ចាស់
        order.delete()

        # ៣. បង្កើត Order ថ្មី (កែត្រង់ចំណុចនេះ)
        # ដោយសារ cashier ជា CharField យើងត្រូវដាក់ .username ដើម្បីយកឈ្មោះជាអក្សរ
        new_order = Order.objects.create(
            cashier=request.user.username, 
            status='CANCEL'
        )

    return redirect('add_item', pk=new_order.pk)
def apply_discount(request, pk):
    if request.method == "POST":
        order = get_object_or_404(Order, pk=pk)
        discount = request.POST.get('discount', 0)
        order.discount_amount = float(discount)
        order.save()
    return redirect('add_item', pk=pk)
def product_list(request):
    """បង្ហាញផលិតផល និងទិន្នន័យ Dashboard នៅលើទំព័រតែមួយ"""
    # ១. ទាញយកទិន្នន័យ
    products = Product.objects.filter(is_active=True) # បង្ហាញតែទំនិញដែលនៅលក់
    all_orders = Order.objects.all() 
    
    # ២. គណនាតួលេខ
    total_sales = all_orders.count()
    total_revenue = sum(order.total for order in all_orders)
    total_products_count = products.count()

    # ៣. រៀបចំ Context ផ្ញើទៅ HTML តែមួយដងគត់
    context = {
        'products': products,
        'total_sales_count': total_sales,
        'total_revenue_today': total_revenue,
        'total_products': total_products_count,
    }
    
    # ៤. Return Render តែម្តងគត់នៅខាងក្រោមគេ
    return render(request, 'sales/product_list.html', context)

def product_detail(request, pk):
    """បង្ហាញព័ត៌មានលម្អិតសម្រាប់ផលិតផលតែមួយ។ Return 404 ប្រសិនបើរកមិនឃើញ"""
    product = get_object_or_404(Product, pk=pk)
    return render(request, 'sales/product_detail.html', {'product': product})

# ឧទាហរណ៍ក្នុង views.py
def checkout(request):
    if request.method == "POST":
        # បង្កើត Order ថ្មី
        order = Order.objects.create(
            cashier=request.user.username, 
            status='paid'  # <--- បន្ថែមបន្ទាត់នេះ ដើម្បីឱ្យវាទៅជា Paid ភ្លាមៗ
        )
        
        # ... កូដសម្រាប់បន្ថែម OrderItem ...
        order.save()
        return redirect('order_success')
def order_list(request):
    """បង្ហាញការបញ្ជាទិញទាំងអស់ ថ្មីបំផុតមុន"""
    orders = Order.objects.all()
    return render(request, 'sales/order_list.html', {'orders': orders})
def product_add(request):
    if request.method == "POST":
        # Get data from the HTML names
        name = request.POST.get('name')
        price = request.POST.get('price')
        stock = request.POST.get('stock')
        category = request.POST.get('category')
        description = request.POST.get('description')
        image = request.FILES.get('image') # Files come from request.FILES

        # Create the product in the database
        Product.objects.create(
            name=name,
            price=price,
            stock=stock,
            category=category,
            description=description,
            image=image
        )
        return redirect('/sales/products/') # Go back to list after saving

    return render(request, 'sales/add_product.html')
@login_required
@login_required
def create_order(request):
    order = Order.objects.create(
        cashier=request.user.username,
        status='paid', # ឬប្រើ 'បានបង់' ឱ្យដូចអ្វីដែលអ្នកចង់បានក្នុង Admin
    )
    return redirect('add_item', pk=order.pk)


@login_required
def add_item(request, pk):
    """
    Let the cashier add line items to an open order, then mark it paid.
    """
    order = get_object_or_404(Order, pk=pk)
    update_id = request.GET.get('update')
    action = request.GET.get('action')

    if update_id and action:
        # 1. Find the specific item in the receipt
        item_to_update = get_object_or_404(OrderItem, id=update_id, order=order)
        
        # 2. Change the quantity
        if action == 'plus':
            item_to_update.quantity += 1
        elif action == 'minus':
            if item_to_update.quantity > 1:
                item_to_update.quantity -= 1
            else:
                # Optional: Delete item if it goes below 1
                item_to_update.delete()
                return redirect('add_item', pk=order.pk)
        
        # 3. Save the change to the database
        item_to_update.save()
        return redirect('add_item', pk=order.pk)
    
    # --- ADD THIS LINE HERE ---
    # This matches the variable name 'products' used in your product_list.html
    products = Product.objects.filter(is_active=True) 

    if request.method == 'POST':
        # "Mark as Paid" button
        if 'mark_paid' in request.POST:
            order.status = 'paid'
            order.save()
            return redirect('order_list')

        # Add a line item
        item_form = OrderItemForm(request.POST)
        if item_form.is_valid():
            item = item_form.save(commit=False)
            item.order      = order
            item.unit_price = item.product.price
            item.save()
            return redirect('add_item', pk=order.pk)
    else:
        item_form = OrderItemForm()

    return render(request, 'sales/add_item.html', {
        'order':     order,
        'item_form': item_form,
        'items':     order.items.select_related('product'),
        'products':  products, # --- AND ADD THIS LINE HERE ---
    })