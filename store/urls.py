"""URL routes for the store app."""
from django.urls import path
from . import views

urlpatterns = [
    
    path('', views.ProductListView.as_view(), name='index'),
    path('product/<int:pk>/', views.product_detail, name='product_detail'),
    path('product/<int:pk>/review/', views.add_review, name='add_review'),
    # cart + checkout (sessions)
    path('cart/', views.cart_view, name='cart'),
    path('cart/add/<int:pk>/', views.add_to_cart, name='add_to_cart'),
    path('cart/remove/<str:key>/', views.remove_from_cart, name='remove_from_cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('orders/', views.order_history, name='order_history'),


    # product CRUD
    path('product/new/', views.product_upload, name='product_upload'),
    path('product/<int:pk>/edit/', views.product_edit, name='product_edit'),
    path('product/<int:pk>/delete/', views.product_delete, name='product_delete'),

    # static pages
    path('about/', views.about, name='about'),

]
