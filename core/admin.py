from django.contrib import admin
from django.utils.html import format_html
from .models import (
    Category, SubCategory, Brand, Product, ProductImage,
    ProductAttribute, ProductAttributeValue, ProductVariant,
    ProductVariantAttribute, Review, Slide, Testimonial, BlogPost
)

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    fields = ['image', 'alt_text', 'is_main', 'order']

class ProductVariantAttributeInline(admin.TabularInline):
    model = ProductVariantAttribute
    extra = 1
    fields = ['attribute_value']

class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 0
    fields = ['sku', 'price', 'price_adjustment', 'quantity', 'is_active']
    show_change_link = True

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'order', 'is_active', 'products_count']
    list_editable = ['order', 'is_active']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name']
    
    def products_count(self, obj):
        return obj.products.count()
    products_count.short_description = "Товаров"

@admin.register(SubCategory)
class SubCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'order', 'is_active', 'products_count']
    list_editable = ['order', 'is_active']
    list_filter = ['category']
    prepopulated_fields = {'slug': ('name',)}
    
    def products_count(self, obj):
        return obj.products.count()
    products_count.short_description = "Товаров"

@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active']
    list_editable = ['is_active']
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'price', 'quantity', 'is_in_stock', 'is_active', 'is_featured']
    list_editable = ['price', 'quantity', 'is_active', 'is_featured']
    
    # Убрали brand, subcategory можно оставить если используешь
    list_filter = ['category', 'subcategory', 'is_active', 'is_featured', 'is_in_stock']
    
    # Убрали 'sku' из поиска
    search_fields = ['name', 'description', 'characteristics']
    
    prepopulated_fields = {'slug': ('name',)}
    
    readonly_fields = ['created_at', 'updated_at', 'is_in_stock']  # is_in_stock можно сделать readonly, если не хочешь менять вручную
    
    inlines = [ProductImageInline, ProductVariantInline]
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('category', 'subcategory', 'name', 'slug')
        }),
        ('Цена и наличие', {
            'fields': ('price', 'quantity', 'is_in_stock')
        }),
        ('Характеристики и описание', {
            'fields': ('characteristics', 'description')
        }),
        ('Настройки', {
            'fields': ('is_active', 'is_featured', 'order')
        }),
        ('Даты', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    list_display = ['product', 'sku', 'price', 'quantity', 'is_active']
    list_editable = ['price', 'quantity', 'is_active']
    list_filter = ['product', 'is_active']
    search_fields = ['sku']
    inlines = [ProductVariantAttributeInline]

@admin.register(ProductAttribute)
class ProductAttributeAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}

@admin.register(ProductAttributeValue)
class ProductAttributeValueAdmin(admin.ModelAdmin):
    list_display = ['attribute', 'value', 'slug']
    list_filter = ['attribute']
    prepopulated_fields = {'slug': ('value',)}

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['product', 'name', 'rating', 'is_active', 'created_at']
    list_editable = ['is_active']
    list_filter = ['rating', 'is_active']
    search_fields = ['name', 'text']

@admin.register(Slide)
class SlideAdmin(admin.ModelAdmin):
    list_display = ['title', 'order', 'is_active']
    list_editable = ['order', 'is_active']

@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ['name', 'rating', 'is_active', 'order']
    list_editable = ['is_active', 'order']

@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ['title', 'created_at', 'views_count', 'is_active']
    list_editable = ['is_active']
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ['views_count']