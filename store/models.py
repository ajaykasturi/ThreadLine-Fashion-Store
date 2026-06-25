from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse


PROVINCE_CHOICES = [
    ('AB', 'Alberta'), ('BC', 'British Columbia'), ('MB', 'Manitoba'),
    ('NB', 'New Brunswick'), ('NL', 'Newfoundland and Labrador'),
    ('NS', 'Nova Scotia'), ('NT', 'Northwest Territories'), ('NU', 'Nunavut'),
    ('ON', 'Ontario'), ('PE', 'Prince Edward Island'), ('QC', 'Quebec'),
    ('SK', 'Saskatchewan'), ('YT', 'Yukon'),
]


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


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='products/gallery/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['uploaded_at']

    def __str__(self):
        return f'photo for {self.product.name}'


class UserProfile(models.Model):
    # address split into fields (not one text blob) so we can validate postal
    # code and pre-fill checkout from it
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone = models.CharField(max_length=20, blank=True)
    street_address = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100, blank=True)
    province = models.CharField(max_length=100, blank=True, choices=PROVINCE_CHOICES)
    postal_code = models.CharField(max_length=10, blank=True)
    country = models.CharField(max_length=100, blank=True, default='Canada')
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)

    def full_address(self):
        parts = [self.street_address, self.city, self.province,
                 self.postal_code, self.country]
        return ', '.join(p for p in parts if p)

    def __str__(self):
        return f"{self.user.username}'s profile"


class Order(models.Model):
    STATUS_CHOICES = [('Pending', 'Pending'), ('Shipped', 'Shipped'), ('Delivered', 'Delivered')]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    full_name = models.CharField(max_length=200)
    phone = models.CharField(max_length=20, blank=True)
    street_address = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    province = models.CharField(max_length=100, choices=PROVINCE_CHOICES)
    postal_code = models.CharField(max_length=10)
    country = models.CharField(max_length=100, default='Canada')
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def shipping_address(self):
        parts = [self.street_address, self.city, self.province,
                 self.postal_code, self.country]
        return ', '.join(p for p in parts if p)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'Order #{self.pk} by {self.user.username}'


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    size = models.CharField(max_length=20, blank=True)

    def subtotal(self):
        return self.quantity * self.price

    def __str__(self):
        return f'{self.quantity} x {self.product}'


class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField(default=5)  # 1..5
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.rating}★ by {self.user.username} on {self.product}'


class ContactMessage(models.Model):
    name = models.CharField(max_length=150)
    email = models.EmailField()
    subject = models.CharField(max_length=200, blank=True)
    message = models.TextField()
    submitted_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)  # null if sent while logged out

    class Meta:
        ordering = ['-submitted_at']

    def __str__(self):
        return f'{self.name} ({self.email}) on {self.submitted_at:%Y-%m-%d}'
