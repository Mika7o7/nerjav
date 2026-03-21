from django.urls import path
from . import views

urlpatterns = [
    # Главная
    path('', views.index, name='home'),
    
    # Категории и подкатегории
    path('category/<slug:category_slug>/', views.category_detail, name='category_detail'),
    path('category/<slug:category_slug>/<slug:subcategory_slug>/', views.subcategory_detail, name='subcategory_detail'),
    
    # Товары
    path('product/<slug:product_slug>/', views.product_detail, name='product_detail'),
    path('product/quick-view/<int:product_id>/', views.product_quick_view, name='product_quick_view'),
    
    
    path('quick-buy/', views.quick_buy, name='quick_buy'),
    
    path('custom-size-order/', views.custom_size_order, name='custom_size_order'),
  
    
]