from django.http import request
from django.shortcuts import render, get_object_or_404, redirect
from .models import Category, Product, Order, OrderItem
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.db.models import Q
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from .forms import UserUpdateForm
from django.views.generic import ListView, UpdateView
from django.contrib.auth.mixins import UserPassesTestMixin
from django.urls import reverse_lazy

# Create your views here.

def product_list(request, category_slug=None):
    category = None
    categories = Category.objects.all()
    products = Product.objects.all() 

    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=category)
    else:
        products = products.order_by('?')[:6]

    context = {
        'category': category,
        'categories': categories,
        'products': products
    }
    return render(request, 'store/product_list.html', context)

def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    context = {'product': product}
    return render(request, 'store/product_detail.html', context)


def add_to_cart(request, product_id):
    cart = request.session.get('cart', {})

    product_id_str = str(product_id)

    if product_id_str in cart:
        cart[product_id_str] += 1
    else:
        cart[product_id_str] = 1

    messages.success(request, f'¡{Product.objects.get(id=product_id).name} fue añadido a tu carrito!')

    request.session['cart'] = cart

    return redirect('product_list')


def cart_detail(request):
    cart = request.session.get('cart', {})
    
    product_ids = cart.keys()
    
    products = Product.objects.filter(id__in=product_ids)
    
    cart_items = []
    total_price = 0

    for product in products:
        quantity = cart[str(product.id)]
        subtotal = product.price * quantity
        total_price += subtotal
        
        cart_items.append({
            'product': product,
            'quantity': quantity,
            'subtotal': subtotal
        })

    context = {
        'cart_items': cart_items,
        'total_price': total_price
    }
    
    return render(request, 'store/cart_detail.html', context)

def remove_from_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    # El carrito SIEMPRE vive en la sesión antes del checkout, 
    # sin importar si el usuario está autenticado o no.
    cart = request.session.get('cart', {})
    product_id_str = str(product_id)

    if product_id_str in cart:
        # Reducimos cantidad o eliminamos del diccionario de la sesión
        if cart[product_id_str] > 1:
            cart[product_id_str] -= 1
            messages.success(request, f'Se redujo la cantidad de {product.name}.')
        else:
            del cart[product_id_str]
            messages.error(request, f'{product.name} fue eliminado del carrito.')
        
        # CORRECCIÓN: Devolver el stock a la base de datos del catálogo
        product.stock += 1
        product.save()
        
        # Actualizamos la sesión para que Django guarde los cambios
        request.session['cart'] = cart
        request.session.modified = True 

    return redirect('cart_detail')

@login_required(login_url='welcome')
@require_POST
def create_order(request):
    cart = request.session.get('cart', {})
    
    if not cart:
        return redirect('product_list')
        
    order = Order.objects.create(user=request.user)
    
    for product_id, quantity in cart.items():
        product = Product.objects.get(id=product_id)

        if product.stock >= quantity:
            OrderItem.objects.create(
                order=order,
                product=product,
                price=product.price,
                quantity=quantity
            )
            product.stock -= quantity
            product.save()
        else:
            continue
            
        
    request.session['cart'] = {}
    
    return redirect('order_success')

def order_success(request):
    return render(request, 'store/order_success.html')

@login_required(login_url='welcome')
def customer_orders(request):
    orders = Order.objects.filter(user=request.user)
    
    context = {
        'orders': orders
    }
    return render(request, 'store/customer_orders.html', context)


def welcome(request):
    return render(request, 'store/welcome.html')

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Cuenta creada exitosamente. Ahora puedes iniciar sesión.')
            return redirect('login')
    else:
        form = UserCreationForm()
    
    return render(request, 'store/register.html', {'form': form})

@login_required(login_url='welcome')
def profile(request):
    if request.method == 'POST':
        form = UserUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, '¡Tu perfil ha sido actualizado con éxito!')
            return redirect('profile')
    else:
        form = UserUpdateForm(instance=request.user)
        
    context = {
        'user': request.user,
        'form': form
    }
    return render(request, 'store/profile.html', context)

class SellerOrderListView(UserPassesTestMixin, ListView):
    model = Order
    template_name = 'store/seller_order_list.html'
    context_object_name = 'orders'
    
    # Solo mostramos pedidos que ya fueron pagados o completados
    queryset = Order.objects.filter(paid=True).order_by('-created_at')

    # Seguridad: Solo permite el acceso si el usuario es staff (vendedor/admin)
    def test_func(self):
        return self.request.user.is_staff

    # Redirige a la página de inicio si no pasa la prueba
    def handle_no_permission(self):
        return redirect('welcome')

class SellerOrderUpdateView(UserPassesTestMixin, UpdateView):
    model = Order
    fields = ['status'] # Solo permitimos modificar el estado
    template_name = 'store/seller_order_detail.html'
    context_object_name = 'order'
    success_url = reverse_lazy('seller_dashboard') # Redirige a la lista tras guardar

    def test_func(self):
        return self.request.user.is_staff

    def handle_no_permission(self):
        return redirect('welcome')