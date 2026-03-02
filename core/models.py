from django.db import models
from django.urls import reverse
from django.utils.text import slugify

class Category(models.Model):
    """Основная категория"""
    name = models.CharField("Название категории", max_length=200)
    slug = models.SlugField("URL", max_length=200, unique=True)
    image = models.ImageField("Изображение", upload_to='categories/', blank=True, null=True)
    description = models.TextField("Описание", blank=True)
    is_active = models.BooleanField("Активна", default=True)
    order = models.PositiveIntegerField("Порядок", default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"
        ordering = ['order', 'name']

    @property
    def product_count(self):
        """Количество товаров в категории и всех подкатегориях"""
        from django.db.models import Count, Q
        return Product.objects.filter(
            Q(category=self) | Q(subcategory__category=self),
            is_active=True
        ).count()

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class SubCategory(models.Model):
    """Подкатегория"""
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='subcategories', verbose_name="Категория")
    name = models.CharField("Название подкатегории", max_length=200)
    slug = models.SlugField("URL", max_length=200, unique=True)
    image = models.ImageField("Изображение", upload_to='subcategories/', blank=True, null=True)
    description = models.TextField("Описание", blank=True)
    is_active = models.BooleanField("Активна", default=True)
    order = models.PositiveIntegerField("Порядок", default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Подкатегория"
        verbose_name_plural = "Подкатегории"
        ordering = ['order', 'name']

    @property
    def product_count(self):
        """Количество товаров в подкатегории"""
        return self.products.filter(is_active=True).count()

    def __str__(self):
        return f"{self.category.name} - {self.name}"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Brand(models.Model):
    """Бренд"""
    name = models.CharField("Название бренда", max_length=200)
    slug = models.SlugField("URL", max_length=200, unique=True)
    logo = models.ImageField("Логотип", upload_to='brands/', blank=True, null=True)
    description = models.TextField("Описание", blank=True)
    website = models.URLField("Сайт", blank=True)
    is_active = models.BooleanField("Активен", default=True)

    class Meta:
        verbose_name = "Бренд"
        verbose_name_plural = "Бренды"

    def __str__(self):
        return self.name


class Product(models.Model):
    """Товар"""
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products', verbose_name="Категория")
    subcategory = models.ForeignKey(SubCategory, on_delete=models.CASCADE, related_name='products', verbose_name="Подкатегория", blank=True, null=True)
    brand = models.ForeignKey(Brand, on_delete=models.SET_NULL, related_name='products', verbose_name="Бренд", blank=True, null=True)
    
    name = models.CharField("Название товара", max_length=500)
    slug = models.SlugField("URL", max_length=500, unique=True)
    sku = models.CharField("Артикул (SKU)", max_length=100, unique=True)
    model = models.CharField("Модель", max_length=200, blank=True)
    
    price = models.DecimalField("Цена", max_digits=10, decimal_places=2)
    tax_price = models.DecimalField("Цена без налога", max_digits=10, decimal_places=2, blank=True, null=True)
    reward_points = models.PositiveIntegerField("Бонусные баллы", default=0)
    
    quantity = models.PositiveIntegerField("Количество на складе", default=0)
    is_in_stock = models.BooleanField("В наличии", default=True)
    
    short_description = models.TextField("Краткое описание", max_length=500, blank=True)
    description = models.TextField("Полное описание", blank=True)
    
    views_count = models.PositiveIntegerField("Просмотры", default=0)
    sold_count = models.PositiveIntegerField("Продано", default=0)
    
    is_active = models.BooleanField("Активен", default=True)
    is_featured = models.BooleanField("Рекомендуемый", default=False)
    order = models.PositiveIntegerField("Порядок", default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Товар"
        verbose_name_plural = "Товары"
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('product_detail', args=[self.slug])

    @property
    def main_image(self):
        return self.images.filter(is_main=True).first()

    @property
    def discount_percent(self):
        if self.tax_price and self.price and self.tax_price < self.price:
            return int((1 - self.tax_price / self.price) * 100)
        return 0
    
    @property
    def average_rating(self):
        reviews = self.reviews.filter(is_active=True)
        if reviews:
            return sum(r.rating for r in reviews) / reviews.count()
        return 0


class ProductImage(models.Model):
    """Изображения товара"""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images', verbose_name="Товар")
    image = models.ImageField("Изображение", upload_to='products/')
    alt_text = models.CharField("Alt текст", max_length=200, blank=True)
    is_main = models.BooleanField("Главное изображение", default=False)
    order = models.PositiveIntegerField("Порядок", default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Изображение товара"
        verbose_name_plural = "Изображения товаров"
        ordering = ['order']

    def __str__(self):
        return f"Изображение для {self.product.name}"

    def save(self, *args, **kwargs):
        if self.is_main:
            ProductImage.objects.filter(product=self.product).update(is_main=False)
        super().save(*args, **kwargs)


class ProductAttribute(models.Model):
    """Атрибуты товара"""
    name = models.CharField("Название атрибута", max_length=100)
    slug = models.SlugField("URL", max_length=100, unique=True)

    class Meta:
        verbose_name = "Атрибут"
        verbose_name_plural = "Атрибуты"

    def __str__(self):
        return self.name


class ProductAttributeValue(models.Model):
    """Значения атрибута"""
    attribute = models.ForeignKey(ProductAttribute, on_delete=models.CASCADE, related_name='values', verbose_name="Атрибут")
    value = models.CharField("Значение", max_length=100)
    slug = models.SlugField("URL", max_length=100)

    class Meta:
        verbose_name = "Значение атрибута"
        verbose_name_plural = "Значения атрибутов"
        unique_together = ('attribute', 'value')

    def __str__(self):
        return f"{self.attribute.name}: {self.value}"


class ProductVariant(models.Model):
    """Варианты товара"""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='variants', verbose_name="Товар")
    
    sku = models.CharField("Артикул", max_length=100, unique=True)
    price = models.DecimalField("Цена", max_digits=10, decimal_places=2, default=0)
    price_adjustment = models.DecimalField("Изменение цены", max_digits=10, decimal_places=2, default=0)
    quantity = models.PositiveIntegerField("Количество", default=0)
    is_active = models.BooleanField("Активен", default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Вариант товара"
        verbose_name_plural = "Варианты товаров"

    def __str__(self):
        return f"{self.product.name} - {self.sku}"

    @property
    def final_price(self):
        return self.price + self.price_adjustment


class ProductVariantAttribute(models.Model):
    """Связь варианта товара с атрибутами (отдельная модель для избежания рекурсии)"""
    variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE, related_name='variant_attributes', verbose_name="Вариант")
    attribute_value = models.ForeignKey(ProductAttributeValue, on_delete=models.CASCADE, related_name='variant_attributes', verbose_name="Значение атрибута")

    class Meta:
        verbose_name = "Атрибут варианта"
        verbose_name_plural = "Атрибуты вариантов"
        unique_together = ('variant', 'attribute_value')

    def __str__(self):
        return f"{self.variant} - {self.attribute_value}"


class Review(models.Model):
    """Отзывы на товар"""
    RATING_CHOICES = [(i, str(i)) for i in range(1, 6)]
    
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews', verbose_name="Товар")
    name = models.CharField("Имя", max_length=200)
    email = models.EmailField("Email")
    rating = models.PositiveSmallIntegerField("Оценка", choices=RATING_CHOICES)
    title = models.CharField("Заголовок", max_length=200, blank=True)
    text = models.TextField("Текст отзыва")
    is_active = models.BooleanField("Активен", default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Отзыв"
        verbose_name_plural = "Отзывы"
        ordering = ['-created_at']

    def __str__(self):
        return f"Отзыв на {self.product.name} от {self.name}"


class Slide(models.Model):
    """Слайды для главной страницы"""
    title = models.CharField("Заголовок", max_length=200)
    description = models.CharField("Описание", max_length=200, blank=True)
    details = models.TextField("Детали", blank=True)
    image = models.ImageField("Изображение", upload_to='slides/')
    link = models.CharField("Ссылка", max_length=200, default='#')
    discount = models.CharField("Скидка", max_length=50, blank=True)
    order = models.PositiveIntegerField("Порядок", default=0)
    is_active = models.BooleanField("Активен", default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Слайд"
        verbose_name_plural = "Слайды"
        ordering = ['order']

    def __str__(self):
        return self.title


class Testimonial(models.Model):
    """Отзывы клиентов"""
    name = models.CharField("Имя", max_length=200)
    position = models.CharField("Должность", max_length=200, blank=True)
    title = models.CharField("Заголовок", max_length=200)
    text = models.TextField("Текст отзыва")
    rating = models.PositiveSmallIntegerField("Оценка", default=5, choices=[(i, i) for i in range(1, 6)])
    image = models.ImageField("Фото", upload_to='testimonials/', blank=True, null=True)
    is_active = models.BooleanField("Активен", default=True)
    order = models.PositiveIntegerField("Порядок", default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Отзыв клиента"
        verbose_name_plural = "Отзывы клиентов"
        ordering = ['order']

    def __str__(self):
        return f"{self.name} - {self.title}"


class BlogPost(models.Model):
    """Статьи в блоге"""
    title = models.CharField("Заголовок", max_length=200)
    slug = models.SlugField("URL", max_length=200, unique=True)
    short_description = models.CharField("Краткое описание", max_length=300)
    content = models.TextField("Содержание")
    image = models.ImageField("Изображение", upload_to='blog/')
    is_active = models.BooleanField("Активен", default=True)
    views_count = models.PositiveIntegerField("Просмотры", default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Статья"
        verbose_name_plural = "Статьи"
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('blog_detail', args=[self.id])
    

class OrderRequest(models.Model):
    """Заявка на покупку (быстрый заказ)"""
    product = models.ForeignKey('Product', on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Товар")
    name = models.CharField("Имя", max_length=150)
    surname = models.CharField("Фамилия", max_length=150, blank=True)
    phone = models.CharField("Телефон", max_length=50)
    telegram = models.CharField("Telegram ник", max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_processed = models.BooleanField("Обработана", default=False)

    class Meta:
        verbose_name = "Заявка на покупку"
        verbose_name_plural = "Заявки на покупку"
        ordering = ['-created_at']

    def __str__(self):
        return f"Заявка от {self.name} {self.surname} — {self.phone}"