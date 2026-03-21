import json
import requests
import logging
import pytz
from django.utils import timezone
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.utils.translation import activate
from django.db.models import F
from .models import (
    Category, SubCategory, Product, Brand, 
    Slide, Testimonial, BlogPost, OrderRequest,
)

# ==================== ОСНОВНЫЕ СТРАНИЦЫ ====================


logger = logging.getLogger(__name__)

@require_POST
@csrf_exempt
def custom_size_order(request):
    """Заявка на индивидуальный размер"""
    try:
        body_data = request.body
        try:
            data = json.loads(body_data)
        except json.JSONDecodeError:
            data = request.POST.dict()

        logger.info(f"Получена заявка на свой размер: {data}")

        # Обязательные поля
        product_id   = data.get('product_id')
        name         = data.get('name')
        phone        = data.get('phone')
        comment      = data.get('comment', '').strip()

        if not product_id:
            return JsonResponse({'success': False, 'message': 'Не указан товар'})
        if not name:
            return JsonResponse({'success': False, 'message': 'Укажите имя'})
        if not phone:
            return JsonResponse({'success': False, 'message': 'Укажите телефон'})
        if not comment:
            return JsonResponse({'success': False, 'message': 'Опишите желаемые характеристики'})

        # Получаем название товара (если есть модель)
        try:
            product = Product.objects.get(id=product_id)
            product_name = product.name
        except (Product.DoesNotExist, ImportError):
            product_name = f"Товар #{product_id}"

        # Московское время
        moscow_tz = pytz.timezone('Europe/Moscow')
        moscow_time = timezone.now().astetimezone(moscow_tz)

        # Формируем красивое сообщение
        message = f"""
            🛠 НОВАЯ ЗАЯВКА НА СВОЙ РАЗМЕР
            👤 Имя: {name}
            📞 Телефон: {phone}
            🆔 ID товара: {product_id}
            📦 Товар: {product_name}
            📝 Пожелания / размер:
            {comment}
            ⏰ Время: {moscow_time.strftime('%d.%m.%Y %H:%M')} (МСК)
        """.strip()

        # Отправляем в Telegram
        telegram_result = send_telegram_message(message)

        if telegram_result:
            return JsonResponse({
                'success': True,
                'message': 'Заявка отправлена! Скоро с вами свяжемся.'
            })
        else:
            return JsonResponse({
                'success': True,
                'message': 'Заявка принята, но возникла проблема с уведомлением. Мы всё равно свяжемся.'
            })

    except Exception as e:
        logger.error(f"Ошибка в custom_size_order: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': 'Произошла ошибка при обработке заявки'
        }, status=500)
    

@require_POST
@csrf_exempt
def quick_buy(request):
    """Быстрый заказ товара"""
    try:
        # Важно! Читаем тело запроса ТОЛЬКО ОДИН РАЗ
        # И сохраняем в переменную
        body_data = request.body
        
        # Пытаемся распарсить как JSON
        try:
            data = json.loads(body_data)
        except json.JSONDecodeError:
            # Если не JSON, пробуем как POST данные
            if hasattr(request, '_body'):
                request._body = body_data
            data = request.POST.dict()
        
        logger.info(f"Получены данные: {data}")
        
        # Валидация
        product_id = data.get('product_id')
        name = data.get('name')
        phone = data.get('phone')
        surname = data.get('surname', '')
        telegram_nick = data.get('telegram', '')
        
        if not product_id:
            return JsonResponse({
                'success': False,
                'message': 'Укажите товар'
            })
        
        if not name:
            return JsonResponse({
                'success': False,
                'message': 'Укажите ваше имя'
            })
        
        if not phone:
            return JsonResponse({
                'success': False,
                'message': 'Укажите номер телефона'
            })
        
        # Получаем товар
        try:
            from .models import Product
            product = Product.objects.get(id=product_id)
            product_name = product.name
        except (ImportError, Product.DoesNotExist):
            product_name = f"Товар #{product_id}"
        
        # Получаем московское время (правильный способ)
        moscow_tz = pytz.timezone('Europe/Moscow')
        moscow_time = timezone.now().astimezone(moscow_tz)
        
        # Формируем сообщение для Telegram
        message = f"""
            🔔 НОВЫЙ БЫСТРЫЙ ЗАКАЗ

            👤 Имя: {name} {surname}
            📞 Телефон: {phone}
            📱 Telegram: {telegram_nick or 'не указан'}
            🆔 ID товара: {product_id}
            📦 Товар: {product_name}

            ⏰ Время: {moscow_time.strftime('%d.%m.%Y %H:%M')} (МСК)
        """
        
        # Отправляем в Telegram
        telegram_result = send_telegram_message(message)
        
        if telegram_result:
            return JsonResponse({
                'success': True,
                'message': 'Спасибо! Ваша заявка принята. Мы свяжемся с вами в ближайшее время.'
            })
        else:
            return JsonResponse({
                'success': True,
                'message': 'Заявка принята. Мы свяжемся с вами.'
            })
            
    except Exception as e:
        logger.error(f"Ошибка в quick_buy: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        
        return JsonResponse({
            'success': False,
            'message': 'Произошла ошибка при обработке заказа'
        })

def send_telegram_message(text):
    """Отправка сообщения в Telegram"""
    try:
        TOKEN = "1625085576:AAGR1VzsLToXxe5NxiPGA-IZy1NmQlbNX7U"
        CHAT_ID = "-1003562137091"
        
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        
        data = {
            'chat_id': CHAT_ID,
            'text': text,
            'parse_mode': 'HTML'
        }
        
        response = requests.post(url, data=data, timeout=10)
        
        if response.status_code == 200:
            logger.info("Telegram сообщение отправлено")
            return True
        else:
            logger.error(f"Ошибка Telegram: {response.text}")
            return False
            
    except Exception as e:
        logger.error(f"Ошибка отправки в Telegram: {str(e)}")
        return False

def index(request):
    """Главная страница"""
    # Получаем категории для меню в шапке
    header_categories = Category.objects.filter(is_active=True).prefetch_related('subcategories')[:10]

    context = {
        'slides': Slide.objects.filter(is_active=True).order_by('order'),
        'categories': Category.objects.filter(is_active=True).prefetch_related('products')[:8],
        'header_categories': header_categories,

        'latest_products': Product.objects.filter(is_active=True).order_by('-created_at'),

        # Варианты замены для bestseller_products (sold_count больше нет)
        # Вариант А: самые новые товары (уже есть latest_products)
        # Вариант Б: товары с наибольшим количеством на складе (quantity)
        # Вариант В: товары, помеченные как is_featured
        'bestseller_products': Product.objects.filter(
            is_active=True,
            is_featured=True
        ).order_by('-created_at'),   # ← пример: рекомендуемые товары

        # special_products — раньше использовался tax_price (скидка)
        # Теперь можно:
        #   - просто новые товары
        #   - или товары с is_featured
        #   - или вообще убрать этот блок
        'special_products': Product.objects.filter(
            is_active=True,
            is_featured=True
        ).order_by('-created_at'),

        
    }
    return render(request, 'core/index.html', context)

def category_detail(request, category_slug):
    """Страница категории"""
    category = get_object_or_404(Category, slug=category_slug, is_active=True)
    products = Product.objects.filter(category=category, is_active=True)
    subcategories = category.subcategories.filter(is_active=True)
    
    context = {
        'category': category,
        'subcategories': subcategories,
        'products': products,
    }
    return render(request, 'core/category_detail.html', context)

def subcategory_detail(request, category_slug, subcategory_slug):

    header_categories = Category.objects.filter(is_active=True).prefetch_related('subcategories')[:10]

    """Страница подкатегории"""
    category = get_object_or_404(Category, slug=category_slug, is_active=True)
    subcategory = get_object_or_404(SubCategory, slug=subcategory_slug, category=category, is_active=True)
    products = Product.objects.filter(subcategory=subcategory, is_active=True)
    
    
    context = {
        'category': category,
        'latest_products': Product.objects.filter(is_active=True)[:10],
        'header_categories': header_categories,
        'subcategory': subcategory,
        'products': products,
    }
    return render(request, 'core/subcategory_detail.html', context)

def product_detail(request, product_slug):
    """Детальная страница товара"""
    product = get_object_or_404(Product, slug=product_slug, is_active=True)
    
   
    
    # Получаем варианты товара
    variants = product.variants.filter(is_active=True).prefetch_related('attributes__attribute')
    
    # Группируем атрибуты
    attributes = {}
    for variant in variants:
        for attr_value in variant.attributes.all():
            attr_name = attr_value.attribute.name
            if attr_name not in attributes:
                attributes[attr_name] = []
            if attr_value not in attributes[attr_name]:
                attributes[attr_name].append(attr_value)
    
    # Похожие товары
    related_products = Product.objects.filter(
        category=product.category, 
        is_active=True
    ).exclude(id=product.id)[:6]
    
    # Отзывы
    reviews = product.reviews.filter(is_active=True)
    
    # ✅ Добавляем категории для меню
    header_categories = Category.objects.filter(is_active=True).prefetch_related('subcategories')[:10]
    
    context = {
        'product': product,
        'variants': variants,
        'attributes': attributes,
        'related_products': related_products,
        'reviews': reviews,
        # ✅ Добавлено в контекст
        'header_categories': header_categories,
    }
    return render(request, 'core/product_detail.html', context)

    



# ==================== API / AJAX ====================

def product_quick_view(request, product_id):
    """Быстрый просмотр товара (AJAX)"""
    product = get_object_or_404(Product, id=product_id, is_active=True)
    data = {
        'id': product.id,
        'name': product.name,
        'price': str(product.price),
        'description': product.short_description,
        'image': product.main_image.image.url if product.main_image else '',
    }
    return JsonResponse(data)
