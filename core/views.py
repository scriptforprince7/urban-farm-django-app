from django.contrib import messages
from django.shortcuts import redirect, render
from django.http import HttpResponse, JsonResponse
from django.template.loader import render_to_string
from core.models import *
from django.urls import reverse
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from paypal.standard.forms import PayPalPaymentsForm
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.http import Http404
import os
import requests
from django.db.models import Case, When, Value, IntegerField
from django.views.generic import View
import razorpay
from django.db import transaction


def index(request):
    main_categories = Main_category.objects.all()

    halfway_index = len(main_categories) // 2

    first_half_categories = main_categories[:halfway_index]
    second_half_categories = main_categories[halfway_index:]

    context = {
        "main_cat": main_categories,
        "first_half_categories": first_half_categories,
        "second_half_categories": second_half_categories,
    }
    return render(request, 'core/index.html', context)


def category(request, main_title):
    main_categories = Main_category.objects.get(main_title=main_title)
    products = Product.objects.filter(main_category=main_categories)
    product_images = ProductImages.objects.filter(product__in=products)
    
    materials = Product.objects.filter(main_category=main_categories).values_list('material', flat=True).distinct()

    selected_material = request.GET.get('material')
    if selected_material:
        products = products.filter(material=selected_material)

    prices = products.values_list('price', flat=True)
    min_price = min(prices) if prices else 0
    max_price = max(prices) if prices else 0

    price_range = request.GET.get('price_range')
    if price_range:
        min_price, max_price = map(float, price_range.split(','))
        products = products.filter(price__range=(min_price, max_price))
    
    context = {
        "main_categories": main_categories,
        "products": products,
        "product_images": product_images,
        "min_price": min_price,
        "max_price": max_price,
    }
    
    if materials:
        context["materials"] = materials

    return render(request, "core/category.html", context)


def main_category(request):
    return render(request, "core/main_category.html")

def checkout(request):
    return render(request, "core/checkout.html")

def confirmation(request):
    return render(request, "core/confirmation.html")


def add_to_cart(request):
    cart_product = {}
    cart_product[str(request.GET['id'])] = {
        'title': request.GET['title'],
        'qty': request.GET['qty'],
        'price': request.GET['price'],
        'image': request.GET['image'],
        'sku': request.GET['sku'],
    }

    if 'cart_data_obj' in request.session:
        if str(request.GET['id']) in request.session['cart_data_obj']:
            cart_data = request.session['cart_data_obj']
            cart_data[str(request.GET['id'])]['qty'] = int(cart_product[str(request.GET['id'])]['qty'])
            request.session['cart_data_obj'] = cart_data
        else:
            cart_data = request.session['cart_data_obj']
            cart_data.update(cart_product)
            request.session['cart_data_obj'] = cart_data
    else:
        request.session['cart_data_obj'] = cart_product

    return JsonResponse({"data": request.session['cart_data_obj'], 'totalcartitems': len(request.session['cart_data_obj'])})


def cart_view(request):
    cart_total_amount = 0
    if 'cart_data_obj' in request.session:
        for p_id, item in request.session['cart_data_obj'].items():
            cart_total_amount += int(item['qty']) * float(item['price'])

        return render(request, "core/cart.html", {"cart_data": request.session['cart_data_obj'], 'totalcartitems': len(request.session['cart_data_obj']), 'cart_total_amount': cart_total_amount})
    else:
        messages.warning(request, "Your cart is empty")
        return redirect("core:main_category")


def search_view(request):
    query = request.GET.get("q")

    products = Product.objects.filter(title__icontains=query).order_by("-date")
    related_main_categories = Main_category.objects.filter(product__in=products).distinct()
    product_images = ProductImages.objects.filter(product__in=products)
    
    total_products_count = Product.objects.count()
    if total_products_count == 0:
        percentage = 0
    else:
        percentage = (products.count() / total_products_count) * 100

    context = {
        "products": products,
        "query": query,
        "related_main_categories": related_main_categories,
        "percentage": percentage, 
        "product_images": product_images,
    }

    return render(request, "core/search.html", context)

def delete_item_from_cart(request):
    product_id = str(request.GET['id'])
    if 'cart_data_obj' in request.session:
        if product_id in request.session['cart_data_obj']:
           cart_data = request.session['cart_data_obj']
           del request.session['cart_data_obj'][product_id]
           request.session['cart_data_obj'] = cart_data

    cart_total_amount = 0
    if 'cart_data_obj' in request.session:
        for p_id, item in request.session['cart_data_obj'].items():
            cart_total_amount += int(item['qty']) * float(item['price'])


    context = render_to_string("core/async/cart-list.html", {"cart_data": request.session['cart_data_obj'], 'totalcartitems': len(request.session['cart_data_obj']), 'cart_total_amount': cart_total_amount})
    return JsonResponse({"data": context, 'totalcartitems': len(request.session['cart_data_obj'])})        


def update_cart(request):
    product_id = str(request.GET['id'])
    product_qty = request.GET['qty']
    if 'cart_data_obj' in request.session:
        if product_id in request.session['cart_data_obj']:
           cart_data = request.session['cart_data_obj']
           cart_data[str(request.GET['id'])]['qty'] = product_qty
           request.session['cart_data_obj'] = cart_data

    cart_total_amount = 0
    if 'cart_data_obj' in request.session:
        for p_id, item in request.session['cart_data_obj'].items():
            cart_total_amount += int(item['qty']) * float(item['price'])


    context = render_to_string("core/async/cart-list.html", {"cart_data": request.session['cart_data_obj'], 'totalcartitems': len(request.session['cart_data_obj']), 'cart_total_amount': cart_total_amount})
    return JsonResponse({"data": context, 'totalcartitems': len(request.session['cart_data_obj'])}) 


@login_required
def checkout_view(request):
    cart_total_amount = 0

    if 'cart_data_obj' in request.session:
        with transaction.atomic():
            for p_id, item in request.session['cart_data_obj'].items():
                cart_total_amount += int(item['qty']) * float(item['price'])
                product = Product.objects.get(pid=p_id) 
                client = razorpay.Client(auth=(settings.KEY, settings.SECRET))
                payment = client.order.create({'amount': int(item['qty']) * float(item['price']) * 100, 'currency': 'INR', 'payment_capture': 1})
                product.razor_pay_order_id = payment['id']
                product.save()

    client = razorpay.Client(auth=(settings.KEY, settings.SECRET))
    payment = client.order.create({'amount': cart_total_amount * 100, 'currency': 'INR', 'payment_capture': 1})

    print(payment)

    context = {
        "payment": payment,
    }

    return render(request, "core/checkout.html", {'cart_data': request.session.get('cart_data_obj', {}),
                                                  'totalcartitems': len(request.session.get('cart_data_obj', {})),
                                                  'cart_total_amount': cart_total_amount,
                                                  **context})


@login_required
def payment_completed_view(request):
    cart_total_amount = 0
    if 'cart_data_obj' in request.session:
        for p_id, item in request.session['cart_data_obj'].items():
            cart_total_amount += int(item['qty']) * float(item['price'])
    return render(request, "core/payment-completed.html")

@login_required
def payment_failed_view(request):
    return render(request, "core/payment-failed.html")


def about(request):
    return render(request, "core/about-us.html")

def contact(request):
    return render(request, "core/contact_us.html")

def career(request):
    return render(request, "core/career.html")

def write_to_ceo(request):
    return render(request, "core/write-to-ceo.html")

def blogs(request):
    return render(request, "core/blog.html")

def privacypolicy(request):
    privacy_policy = PrivacyPolicy.objects.first()  # Assuming you have a PrivacyPolicy instance
    context = {
        'privacy_policy_content': privacy_policy.privacy_policy_content if privacy_policy else ''
    }
    return render(request, 'core/privacy-policy.html', context)

class RobotsTxtView(View):
    def get(self, request, *args, **kwargs):
        # Specify the path to your robots.txt file
        robots_txt_path = os.path.join(settings.BASE_DIR, 'static', 'robots.txt')

        with open(robots_txt_path, 'r') as f:
            content = f.read()

        return HttpResponse(content, content_type='text/plain')
    
def product_new(request, title):
    product = Product.objects.get(title=title)
    product_variants = ProductVarient.objects.filter(product=product)
    product_variant_types = ProductVariantTypes.objects.filter(product_variant__in=product_variants)
    product_images = ProductImages.objects.filter(product=product)

    context = {
        "products": product,
        "product_variants": product_variants,
        "product_variant_types": product_variant_types,
        "product_images": product_images,
    }

    return render(request, "core/product.html", context)