from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import ListView
from django.db.models import Q

from .models import Product, Category, Order, OrderItem, Review, UserProfile, ContactMessage, ProductImage
from .forms import (RegisterForm, ProfileForm, ProductForm, CheckoutForm,
                    ReviewForm, ContactForm, ChangePasswordForm)



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


# ---------------------------------------------------------------
# PRODUCT CRUD  (registered users manage their own products)
# ---------------------------------------------------------------
@login_required
def product_upload(request):
    if not request.user.is_staff:
        messages.error(request, 'Only staff can add products.')
        return redirect('index')
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.uploaded_by = request.user
            product.save()
            for f in request.FILES.getlist('extra_images'):
                ProductImage.objects.create(product=product, image=f)
            messages.success(request, 'Product uploaded!')
            return redirect('product_detail', pk=product.pk)
    else:
        form = ProductForm()
    return render(request, 'store/product_form.html', {'form': form, 'title': 'Upload Product'})


@login_required
def product_edit(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if not request.user.is_staff:
        messages.error(request, 'Only staff can edit products.')
        return redirect('product_detail', pk=pk)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            for f in request.FILES.getlist('extra_images'):
                ProductImage.objects.create(product=product, image=f)
            messages.success(request, 'Product updated.')
            return redirect('product_detail', pk=pk)
    else:
        form = ProductForm(instance=product)
    return render(request, 'store/product_form.html', {'form': form, 'title': 'Edit Product', 'product': product})


def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)

    recently = request.session.get('recently_viewed', [])
    if pk in recently:
        recently.remove(pk)
    recently.insert(0, pk)                       # newest first
    recently = recently[:5]                       # keep last 5
    request.session['recently_viewed'] = recently
    request.session.modified = True

    recent_products = Product.objects.filter(pk__in=recently[1:5]).exclude(pk=pk)
    review_form = ReviewForm()
    return render(request, 'store/product_detail.html', {
        'product': product,
        'recent_products': recent_products,
        'reviews': product.reviews.all(),
        'review_form': review_form,
    })


@login_required
def add_review(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.product = product
            review.user = request.user
            review.save()
            messages.success(request, 'Review posted!')
    return redirect('product_detail', pk=pk)


# ---------------------------------------------------------------
# CART
# Lives entirely in request.session so guests can use it too; checkout
# itself is gated to registered users below.
# ---------------------------------------------------------------
def _get_cart(request):
    return request.session.get('cart', {})   # { "product_id:size": quantity }


def add_to_cart(request, pk):
    product = get_object_or_404(Product, pk=pk)
    sizes = product.size_list()
    size = request.POST.get('size', '')
    if size not in sizes:
        size = sizes[0] if sizes else 'Regular'
    key = f'{pk}:{size}'
    cart = _get_cart(request)
    cart[key] = cart.get(key, 0) + 1
    request.session['cart'] = cart
    request.session.modified = True
    messages.success(request, f'Added "{product.name}" ({size}) to cart.')
    return redirect(request.META.get('HTTP_REFERER', 'index'))


def cart_view(request):
    cart = _get_cart(request)
    items, total = [], Decimal('0')
    for key, qty in cart.items():
        pid, _, size = key.partition(':')
        product = Product.objects.filter(pk=pid).first()
        if product:
            subtotal = product.price * qty
            total += subtotal
            items.append({'product': product, 'size': size, 'qty': qty,
                          'subtotal': subtotal, 'key': key})
    return render(request, 'store/cart.html', {'items': items, 'total': total})


def remove_from_cart(request, key):
    cart = _get_cart(request)
    cart.pop(key, None)
    request.session['cart'] = cart
    request.session.modified = True
    return redirect('cart')


@login_required
def checkout(request):
    cart = _get_cart(request)
    if not cart:
        messages.warning(request, 'Your cart is empty.')
        return redirect('index')

    items, total = [], Decimal('0')
    for key, qty in cart.items():
        pid, _, size = key.partition(':')
        product = Product.objects.filter(pk=pid).first()
        if product:
            items.append((product, size, qty))
            total += product.price * qty

    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.user = request.user
            order.total = total
            order.save()
            for product, size, qty in items:
                OrderItem.objects.create(order=order, product=product,
                                         quantity=qty, price=product.price, size=size)
            request.session['cart'] = {}   # clear cart
            request.session.modified = True
            messages.success(request, f'Order #{order.pk} placed successfully!')
            return redirect('order_history')
    else:
        prof = getattr(request.user, 'profile', None)
        initial = {'full_name': request.user.get_full_name() or request.user.username}
        if prof:
            initial.update({
                'phone': prof.phone, 'street_address': prof.street_address,
                'city': prof.city, 'province': prof.province,
                'postal_code': prof.postal_code,
                'country': prof.country or 'Canada',
            })
        form = CheckoutForm(initial=initial)
    return render(request, 'store/checkout.html', {'form': form, 'items': items, 'total': total})

@login_required
def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if not request.user.is_staff:
        messages.error(request, 'Only staff can delete products.')
        return redirect('product_detail', pk=pk)
    if request.method == 'POST':
        product.delete()
        messages.success(request, 'Product deleted.')
        return redirect('index')
    return render(request, 'store/product_confirm_delete.html', {'product': product})


@login_required
def order_history(request):
    orders = request.user.orders.prefetch_related('items__product')
    return render(request, 'store/order_history.html', {'orders': orders})

def about(request):
    return render(request, 'store/about.html')

def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            msg = form.save(commit=False)
            if request.user.is_authenticated:
                msg.user = request.user      # remember who sent it
            msg.save()
            messages.success(
                request, 'Thanks for reaching out. We have received your message.')
            return redirect('contact')       # redirect so refresh does not resubmit
    else:
        initial = {}
        if request.user.is_authenticated:
            initial = {'name': request.user.get_full_name() or request.user.username,
                       'email': request.user.email}
        form = ContactForm(initial=initial)
    return render(request, 'store/contact.html', {'form': form})
