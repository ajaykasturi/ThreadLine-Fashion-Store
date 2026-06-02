from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)

    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['name']

    def __str__(self):
        return self.name

class Product(models.Model):
    BRAND_CHOICES = [
        ('Nike', 'Nike'), ('Adidas', 'Adidas'), ('Zara', 'Zara'),
        ('H&M', 'H&M'), ('Levis', 'Levis'), ('Puma', 'Puma'), ('Other', 'Other'),
    ]
    name = models.CharField(max_length=200)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    brand = models.CharField(max_length=50, choices=BRAND_CHOICES, default='Other')
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    stock = models.PositiveIntegerField(default=10)
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='uploaded_products')
    created_at = models.DateTimeField(auto_now_add=True)
    sizes = models.CharField(max_length=100, default='Regular', blank=True,
                              help_text='Comma-separated, e.g. S,M,L,XL')

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.name} ({self.brand})'

    def get_absolute_url(self):
        return reverse('product_detail', args=[self.pk])

    def size_list(self):
        return [s.strip() for s in self.sizes.split(',') if s.strip()]
