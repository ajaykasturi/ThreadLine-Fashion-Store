
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView
from django.db.models import Q
from .models import Product, Category

# Create your views here.
class ProductListView(ListView):
    """Homepage. GET params: q (keyword search), category, brand, sort."""
    model = Product
    template_name = 'store/index.html'
    context_object_name = 'products'
    paginate_by = 8

    def get_queryset(self):
        qs = Product.objects.select_related('category').all()
        q = self.request.GET.get('q', '').strip()
        category = self.request.GET.get('category', '')
        brand = self.request.GET.get('brand', '')
        sort = self.request.GET.get('sort', '')

        if q:
            qs = qs.filter(Q(name__icontains=q) | Q(description__icontains=q))
        if category:
            qs = qs.filter(category__slug=category)
        if brand:
            qs = qs.filter(brand=brand)
        if sort == 'low':
            qs = qs.order_by('price')
        elif sort == 'high':
            qs = qs.order_by('-price')
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['categories'] = Category.objects.all()
        ctx['brands'] = [b[0] for b in Product.BRAND_CHOICES]
        # keep current selections so the form stays populated after submit
        ctx['current'] = {
            'q': self.request.GET.get('q', ''),
            'category': self.request.GET.get('category', ''),
            'brand': self.request.GET.get('brand', ''),
            'sort': self.request.GET.get('sort', ''),
        }
        return ctx