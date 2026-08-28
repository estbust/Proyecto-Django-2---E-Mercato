from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    
    class Meta:
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.name

class Product(models.Model):
    category = models.ForeignKey(Category, related_name='products', on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    stock = models.PositiveIntegerField(default=0)
    available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

# Asegúrate de tener: from django.contrib.auth.models import User en la parte superior

class Order(models.Model):
    # Conectamos el pedido al usuario que lo realizó
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    # Un booleano para simular si la pasarela de pago (futura) fue exitosa
    paid = models.BooleanField(default=False) 

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'Pedido {self.id} de {self.user.username}'

class OrderItem(models.Model):
    # Conectamos este "renglón" de la factura con el Pedido general
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    # Conectamos con el Producto exacto que se está comprando
    product = models.ForeignKey(Product, related_name='order_items', on_delete=models.CASCADE)
    
    # ¡CRÍTICO! Guardamos el precio exacto al momento de la compra
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f'{self.quantity}x {self.product.name} (Pedido {self.order.id})'