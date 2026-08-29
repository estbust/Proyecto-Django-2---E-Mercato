from django.http import request
from django.shortcuts import render, get_object_or_404, redirect
from .models import Category, Product, Order, OrderItem
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.db.models import Q
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from .forms import UserUpdateForm

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

    # Escenario A: Usuario Autenticado (Base de datos)
    if request.user.is_authenticated:
        # Buscamos el carrito activo
        order = Order.objects.filter(user=request.user, paid=False).first()
        if order:
            # Buscamos el artículo específico dentro de ese carrito
            order_item = OrderItem.objects.filter(order=order, product=product).first()
            if order_item:
                # Si hay más de 1, restamos 1. Si solo queda 1, eliminamos el artículo completo.
                if order_item.quantity > 1:
                    order_item.quantity -= 1
                    order_item.save()
                    messages.success(request, f'Se redujo la cantidad de {product.name}.')
                else:
                    order_item.delete()
                    messages.error(request, f'{product.name} fue eliminado del carrito.')

    # Escenario B: Usuario Invitado (Sesión/Cookies)
    else:
        cart = request.session.get('cart', {})
        product_id_str = str(product_id)

        if product_id_str in cart:
            if cart[product_id_str] > 1:
                cart[product_id_str] -= 1
                messages.success(request, f'Se redujo la cantidad de {product.name}.')
            else:
                del cart[product_id_str]
                messages.error(request, f'{product.name} fue eliminado del carrito.')
            
            # Guardamos la actualización en la sesión
            request.session['cart'] = cart

    # Redirigimos de vuelta a la página del carrito
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