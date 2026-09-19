from django.contrib.admin import views
from django.urls import path
from .views import product_list, product_detail, add_to_cart, cart_detail, create_order, order_success, customer_orders, welcome, register, profile, remove_from_cart, SellerOrderListView, SellerOrderUpdateView

urlpatterns = [
    path('', product_list, name='product_list'),
    path('categoria/<slug:category_slug>/', product_list, name='product_list_by_category'),
    path('producto/<int:product_id>/', product_detail, name='product_detail'),
    path('agregar/<int:product_id>/', add_to_cart, name='add_to_cart'),
    path('carrito/', cart_detail, name='cart_detail'),
    path('crear-pedido/', create_order, name='create_order'),
    path('pedido-exitoso/', order_success, name='order_success'),
    path('mis-pedidos/', customer_orders, name='customer_orders'),
    path('welcome/', welcome, name='welcome'),
    path('registro/', register, name='register'),
    path('perfil/', profile, name='profile'),
    path('remover/<int:product_id>/', remove_from_cart, name='remove_from_cart'),
    path('panel/pedidos/', SellerOrderListView.as_view(), name='seller_dashboard'),
    path('panel/pedidos/<int:pk>/', SellerOrderUpdateView.as_view(), name='seller_order_detail'),
]