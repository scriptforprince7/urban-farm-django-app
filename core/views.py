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
from datetime import datetime 
from decimal import Decimal, ROUND_HALF_UP
import re
from geopy.geocoders import Nominatim
from django.http import QueryDict
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags    
from num2words import num2words

def index(request):
    main_categories = Main_category.objects.filter(active_status='published')
    new_arrival = Product.objects.filter(new_arrival=True)
    deal_of_week = Product.objects.filter(deal_of_week=True)
    summer_sale = Product.objects.filter(summer_sale=True)
    product_variants = ProductVarient.objects.filter(product__in=deal_of_week)
    product_variant_types = ProductVariantTypes.objects.filter(product_variant__product__in=deal_of_week)
    product_images = ProductImages.objects.filter(product__in=deal_of_week)

    halfway_index = len(main_categories) // 2

    first_half_categories = main_categories[:halfway_index]
    second_half_categories = main_categories[halfway_index:]

    context = {
        "main_cat": main_categories,
        "first_half_categories": first_half_categories,
        "second_half_categories": second_half_categories,
        "new_arrival": new_arrival,
        "deal_of_week": deal_of_week,
        "summer_sale": summer_sale,
        "product_variants": product_variants,
        "product_variant_types": product_variant_types,
        "product_images": product_images,
    }
    return render(request, 'core/index.html', context)

def category(request, main_title):
    main_categories = Main_category.objects.get(main_title=main_title)
    products = Product.objects.filter(main_category=main_categories)
    product_images = ProductImages.objects.filter(product__in=products)

    product_variants = ProductVarient.objects.filter(product__in=products)
    variant_types = ProductVariantTypes.objects.filter(product_variant__in=product_variants)
    
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

    categories = Category.objects.filter(main_category=main_categories)
    
    gst_rate = None  # Initialize gst_rate here

    for product in products:
        # Check if the product has variants
        product_has_variants = product.productvarient_set.exists()

        if product_has_variants:
            # Get the first variant
            first_variant = product.productvarient_set.first()
            # Calculate default price without GST
            price_wo_gst = first_variant.productvarianttypes_set.first().varient_price
            # Fetching GST rate
            gst_rate = first_variant.productvarianttypes_set.first().gst_rate
            # Calculate default price including GST
            base_price = first_variant.productvarianttypes_set.first().varient_price
            # Calculate GST amount
            gst_amount = base_price * Decimal(gst_rate.strip('%')) / 100
            # Calculate total price including GST and round off to two decimal places
            product.gst_inclusive_price = round(base_price + gst_amount, 2)
            # Include original variant price in the context
            product.variant_price = price_wo_gst
        else:
            # Use the existing GST-inclusive price for the product
            product.gst_inclusive_price = product.price * (1 + Decimal(product.gst_rate.strip('%')) / 100)
            gst_rate = product.gst_rate
            # If the product doesn't have variants, set variant_price to None
            product.variant_price = None

    context = {
        "main_categories": main_categories,
        "products": products,
        "product_images": product_images,
        "min_price": min_price,
        "max_price": max_price,
        "categories": categories,
        "product_variants": product_variants,
        "variant_types": variant_types,
        "gst_rate": gst_rate,  # Include gst_rate in the context
    }
    
    if materials:
        context["materials"] = materials

    return render(request, "core/category.html", context)


def main_category(request):
    return render(request, "core/main_category.html")

def checkout(request):
    return render(request, "core/checkout.html")

def payment_failed_view(request):
    return render(request, "core/confirmation-failed.html")


def add_to_cart(request):
    cart_product = {}
    cart_product[str(request.GET['id'])] = {
        'title': request.GET['title'],
        'qty': request.GET['qty'],
        'price': request.GET['price'],
        'image': request.GET['image'],
        'sku': request.GET['sku'],
        'price_wo_gst': request.GET['price_wo_gst'],
        'gst_rate': request.GET['gst_rate'],
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

        return render(request, "core/cart.html", {
            "cart_data": request.session['cart_data_obj'], 
            'totalcartitems': len(request.session['cart_data_obj']), 
            'cart_total_amount': cart_total_amount
        })
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
    total_amount = 0
    price_wo_gst_total = 0
    total_gst = 0
    user_zipcode = request.POST.get("checkout_zipcode")  # Get user's zipcode from the form

    # Define Maharashtra zipcodes
    maharashtra_zipcodes = ["400012", "400067", "400004", "400033", ...]  # Add all Mumbai zipcodes here

    # Check if user's zipcode is in Maharashtra
    if user_zipcode in maharashtra_zipcodes:
        # Maharashtra zipcode logic
        cgst_factor = 0.5  # CGST and SGST will be 50% each
        igst_factor = 0  # IGST will be 0%
    else:
        # Non-Maharashtra zipcode logic
        cgst_factor = 0  # CGST will be 0%
        igst_factor = 1  # IGST will be 100%

    if 'cart_data_obj' in request.session:
        # Calculate total amount, price without GST, and total GST
        for p_id, item in request.session['cart_data_obj'].items():
            total_amount += int(item['qty']) * float(item['price'])
            price_wo_gst_total += int(item['qty']) * float(item.get('price_wo_gst', item['price']))
            item_gst = (Decimal(item['price']) - Decimal(item.get('price_wo_gst', item['price']))) * int(
                item['qty'])  # Calculate GST for this item

            # Calculate CGST, SGST, and IGST for each product based on the user's zipcode
            cgst = item_gst * cgst_factor
            sgst = item_gst * cgst_factor
            igst = item_gst * igst_factor

            total_gst += item_gst  # Add item's GST to total GST

            # Do whatever you want with CGST, SGST, and IGST here

    order = CartOrder.objects.create(
        user=request.user,
        price=total_amount
    )

    for p_id, item in request.session['cart_data_obj'].items():
        cart_total_amount += int(item['qty']) * float(item['price'])

        cart_order_products = CartOrderItems.objects.create(
            order=order,
            invoice_no="order_id-" + str(order.id),
            item=item['title'],
            image=item['image'],
            qty=item['qty'],
            price=item['price'],
            total=float(item['qty']) * float(item['price'])
        )

    cart_total_amount = 0
    if 'cart_data_obj' in request.session:
        with transaction.atomic():
            for p_id, item in request.session['cart_data_obj'].items():
                cart_total_amount += int(item['qty']) * float(item['price'])
                product = Product.objects.get(pid=p_id)
                client = razorpay.Client(auth=(settings.KEY, settings.SECRET))
                payment = client.order.create(
                    {'amount': int(item['qty']) * float(item['price']) * 100, 'currency': 'INR',
                     'payment_capture': 1})
                product.razor_pay_order_id = payment['id']
                product.save()

    client = razorpay.Client(auth=(settings.KEY, settings.SECRET))
    payment = client.order.create({'amount': cart_total_amount * 100, 'currency': 'INR', 'payment_capture': 1})

    context = {
        "payment": payment,
        "price_wo_gst_total": price_wo_gst_total,
        "total_gst": total_gst,
        "user_zipcode": user_zipcode,
        "maharashtra_zipcodes": maharashtra_zipcodes,
    }

    return render(request, "core/checkout.html",
                  {'cart_data': request.session.get('cart_data_obj', {}),
                   'totalcartitems': len(request.session.get('cart_data_obj', {})),
                   'cart_total_amount': cart_total_amount,
                   **context})


@login_required
def payment_failed_view(request):
    return render(request, "core/payment-failed.html")

def about(request):
    return render(request, "core/about-us.html")

def tnc(request):
    return render(request, "core/tnc.html")

def contact(request):
    return render(request, "core/contact_us.html")

def career(request):
    return render(request, "core/career.html")

def write_to_ceo(request):
    return render(request, "core/write-to-ceo.html")

def blogs(request):
    return render(request, "core/blog.html")

@login_required
def payment_invoice(request):
    razorpay_payment_id = request.GET.get('razorpay_payment_id')
    razorpay_order_id = request.GET.get('razorpay_order_id')
    razorpay_signature = request.GET.get('razorpay_signature')

    # Retrieve form data from query parameters
    query_params = request.GET
    first_name = query_params.get('first_name')
    last_name = query_params.get('last_name')
    company_name = query_params.get('company_name')
    gst_number = query_params.get('gst_number')
    zipcode = query_params.get('zipcode')
    city = query_params.get('city')
    street_address = query_params.get('street_address')
    shipping_address = query_params.get('shipping_address')
    phone = query_params.get('phone')
    email = query_params.get('email')
    cart_total_amount = 0
    total_amount = 0
    price_wo_gst_total = 0
    total_gst = 0

    current_datetime = datetime.now() 

    # Define Maharashtra zipcodes
    maharashtra_zipcodes = ["400001", "400002", "400003", "400004", "400005", "400006", "400007", "400008", "400009", "400010", 
                        "400011", "400012", "400013", "400014", "400015", "400016", "400017", "400018", "400019", "400020", 
                        "400021", "400022", "400023", "400024", "400025", "400026", "400027", "400028", "400029", "400030", 
                        "400031", "400032", "400033", "400034", "400035", "400036", "400037", "400038", "400039", "400040", 
                        "400041", "400042", "400043", "400044", "400045", "400046", "400047", "400048", "400049", "400050",
                        "400051", "400052", "400053", "400054", "400055", "400056", "400057", "400058", "400059", "400060", 
                        "400061", "400062", "400063", "400064", "400065", "400066", "400067", "400068", "400069", "400070", 
                        "400071", "400072", "400073", "400074", "400075", "400076", "400077", "400078", "400079", "400080", 
                        "400081", "400082", "400083", "400084", "400085", "400086", "400087", "400088", "400089", "400090", 
                        "400091", "400092", "400093", "400094", "400095", "400096", "400097", "400098", "400099", "400100",
                        "410201", "410202", "410203", "410204", "410205", "410206", "410207", "410208", "410209", "410210",
                        # Add more zip codes as needed
                        ]

    if 'cart_data_obj' in request.session:
    # Initialize dictionaries to store CGST, SGST, and IGST amounts for each product
       cgst_amounts = {}
       sgst_amounts = {}
       igst_amounts = {}
       gst_amounts = {}
       gst_amounts_combined = {}  # Dictionary to store aggregated GST amounts

    # Calculate total amount, price without GST, and total GST
    for p_id, item in request.session['cart_data_obj'].items():
        total_amount += int(item['qty']) * Decimal(item['price'])
        price_wo_gst_total += int(item['qty']) * Decimal(item.get('price_wo_gst', item['price']))
        price_wo_gst_final = int(item['qty']) * Decimal(item.get('price_wo_gst', item['price']))
        item_gst = (Decimal(item['price']) - Decimal(item.get('price_wo_gst', item['price']))) * int(
            item['qty'])  # Calculate GST for this item

        # Calculate GST rates
        if price_wo_gst_final != 0:
            gst_rates_final = (item_gst / price_wo_gst_final) * 100
        else:
            gst_rates_final = Decimal('0')

        item['gst_rates_final'] = gst_rates_final

        # Divide the GST amount by 2 to get CGST and SGST separately
        if zipcode in maharashtra_zipcodes:
            # For Maharashtra zip codes, calculate CGST and SGST separately
            igst_amount = Decimal('0')  # IGST will be 0
            gst_rates_final = gst_rates_final / Decimal(2)
        else:
            # For non-Maharashtra zip codes, IGST will be double of CGST
            igst_amount = item_gst
            gst_rates_final = gst_rates_final
       

        # Aggregate GST amounts based on GST rates
        if gst_rates_final in gst_amounts:
            gst_amounts[gst_rates_final] += item_gst
        else:
            gst_amounts[gst_rates_final] = item_gst

        total_gst += item_gst

    # Print CGST Amounts
    print("CGST Amounts:")
    for gst_rate, total_gst_amount in gst_amounts.items():
        cgst_amount = total_gst_amount / Decimal(2)
        print(f"CGST Amount: {cgst_amount}, GST Rate: {gst_rate}")

    # Print SGST Amounts
    print("\nSGST Amounts:")
    for gst_rate, total_gst_amount in gst_amounts.items():
        sgst_amount = total_gst_amount / Decimal(2)
        print(f"SGST Amount: {sgst_amount}, GST Rate: {gst_rate}")
    
    print("\nIGST Amounts:")
    for gst_rate, total_gst_amount in gst_amounts.items():
        igst_amount = total_gst_amount
        print(f"IGST Amount: {igst_amount}, GST Rate: {gst_rate}")
    
    print("GST Amounts:")
    print(gst_amounts)

    for gst_rate, total_gst_amount in gst_amounts.items():
        cgst_amount = total_gst_amount / Decimal(2)
        sgst_amount = total_gst_amount / Decimal(2)
        gst_amounts_combined[gst_rate] = {'cgst': cgst_amount, 'sgst': sgst_amount}

    order = CartOrder.objects.create(
        user=request.user,
        price=total_amount
    )

    for p_id, item in request.session['cart_data_obj'].items():
        cart_total_amount += int(item['qty']) * float(item['price'])

        cart_order_products = CartOrderItems.objects.create(
            order=order,
            invoice_no="order_id-" + str(order.id),
            item=item['title'],
            image=item['image'],
            qty=item['qty'],
            price=item['price'],
            total=float(item['qty']) * float(item['price'])
        )

    cart_total_amount = 0
    if 'cart_data_obj' in request.session:
        with transaction.atomic():
            for p_id, item in request.session['cart_data_obj'].items():
                cart_total_amount += int(item['qty']) * float(item['price'])
                product = Product.objects.get(pid=p_id)
                client = razorpay.Client(auth=(settings.KEY, settings.SECRET))
                payment = client.order.create(
                    {'amount': int(item['qty']) * float(item['price']) * 100, 'currency': 'INR',
                     'payment_capture': 1})
                product.razor_pay_order_id = payment['id']
                product.save()

    client = razorpay.Client(auth=(settings.KEY, settings.SECRET))
    payment = client.order.create({'amount': cart_total_amount * 100, 'currency': 'INR', 'payment_capture': 1})
    cart_total_amount_rounded = round(cart_total_amount, 2)
    cart_total_amount_words = num2words(cart_total_amount_rounded, lang='en_IN')

    invoice_number, created = InvoiceNumber.objects.get_or_create()

    # Increment the invoice number
    invoice_number.increment()

    # Use the incremented invoice number for the current invoice
    invoice_no = str(invoice_number)

    half_total_gst_amount = total_gst / Decimal(2)

    context = {
    "payment": payment,
    "price_wo_gst_total": price_wo_gst_total,
    "total_gst": total_gst,
    "cgst_amounts": cgst_amounts,
    "sgst_amounts": sgst_amounts,
    "igst_amounts": igst_amounts,
    "zipcode": zipcode,
    "maharashtra_zipcodes": maharashtra_zipcodes,
    'razorpay_payment_id': razorpay_payment_id,
    'razorpay_order_id': razorpay_order_id,
    'razorpay_signature': razorpay_signature,
    'first_name': first_name,
    'last_name': last_name,
    'company_name': company_name,
    'gst_number': gst_number,
    'zipcode': zipcode,
    'city': city,
    'street_address': street_address,
    'phone': phone,
    'email': email,
    "cgst_amount": cgst_amount,
    "sgst_amount": sgst_amount,
    "igst_amount" : igst_amount,
    "igst_amounts" : igst_amounts,
    "gst_rates_final": gst_rates_final,
    "gst_rates_final": gst_rates_final,
    "shipping_address": shipping_address,
    "cart_total_amount_words": cart_total_amount_words,
    'invoice_no': invoice_no,
    "half_total_gst_amount": half_total_gst_amount,
    "gst_amounts": gst_amounts,
    "gst_rate": gst_rate,
    "gst_amounts_combined": gst_amounts_combined,
}
    subject = 'Payment Invoice'
    from_email = 'princesachdeva@nationalmarketingprojects.com'
    to_email = email
    html_message = render_to_string('core/payment_invoice.html', {'context': context})
    plain_message = strip_tags(html_message)

    send_mail(subject, plain_message, from_email, [to_email], html_message=html_message)

    return render(request, "core/payment_invoice.html", {'current_datetime': current_datetime, 'cart_data': request.session.get('cart_data_obj', {}), 'totalcartitems': len(request.session.get('cart_data_obj', {})), 'cart_total_amount': cart_total_amount, **context})


@login_required
def checkout_view(request):
    cart_total_amount = 0
    total_amount = 0
    price_wo_gst_total = 0
    total_gst = 0
    user_zipcode = request.POST.get("checkout_zipcode")  # Get user's zipcode from the form

    # Define Maharashtra zipcodes
    maharashtra_zipcodes = ["400012", "400067", "400004", "400033", ...]  # Add all Mumbai zipcodes here

    # Check if user's zipcode is in Maharashtra
    if user_zipcode in maharashtra_zipcodes:
        # Maharashtra zipcode logic
        cgst_factor = Decimal('0.025')  # CGST rate for Maharashtra (2.5%)
        sgst_factor = Decimal('0.025')  # SGST rate for Maharashtra (2.5%)
        igst_factor = Decimal('0')      # IGST will be 0%
    else:
        # Non-Maharashtra zipcode logic
        cgst_factor = Decimal('0.09')   # CGST rate for other states (9%)
        sgst_factor = Decimal('0.09')   # SGST rate for other states (9%)
        igst_factor = Decimal('1')      # IGST will be 100%

    if 'cart_data_obj' in request.session:
        # Calculate total amount, price without GST, and total GST
        for p_id, item in request.session['cart_data_obj'].items():
            total_amount += int(item['qty']) * float(item['price'])
            price_wo_gst_total += int(item['qty']) * float(item.get('price_wo_gst', item['price']))
            item_gst = (Decimal(item['price']) - Decimal(item.get('price_wo_gst', item['price']))) * int(
                item['qty'])  # Calculate GST for this item

            # Calculate CGST and SGST for each product based on the user's zipcode
            cgst = item_gst * cgst_factor
            sgst = item_gst * sgst_factor
            igst = item_gst * igst_factor

            total_gst += item_gst  # Add item's GST to total GST

            # Do whatever you want with CGST, SGST, and IGST here

    order = CartOrder.objects.create(
        user=request.user,
        price=total_amount
    )

    for p_id, item in request.session['cart_data_obj'].items():
        cart_total_amount += int(item['qty']) * float(item['price'])

        cart_order_products = CartOrderItems.objects.create(
            order=order,
            invoice_no="order_id-" + str(order.id),
            item=item['title'],
            image=item['image'],
            qty=item['qty'],
            price=item['price'],
            total=float(item['qty']) * float(item['price'])
        )

    cart_total_amount = 0
    if 'cart_data_obj' in request.session:
        with transaction.atomic():
            for p_id, item in request.session['cart_data_obj'].items():
                cart_total_amount += int(item['qty']) * float(item['price'])
                product = Product.objects.get(pid=p_id)
                client = razorpay.Client(auth=(settings.KEY, settings.SECRET))
                payment = client.order.create(
                    {'amount': int(item['qty']) * float(item['price']) * 100, 'currency': 'INR',
                     'payment_capture': 1})
                product.razor_pay_order_id = payment['id']
                product.save()

    client = razorpay.Client(auth=(settings.KEY, settings.SECRET))
    payment = client.order.create({'amount': cart_total_amount * 100, 'currency': 'INR', 'payment_capture': 1})

    context = {
        "payment": payment,
        "price_wo_gst_total": price_wo_gst_total,
        "total_gst": total_gst,
        "user_zipcode": user_zipcode,
        "maharashtra_zipcodes": maharashtra_zipcodes,
    }

    return render(request, "core/checkout.html",
                  {'cart_data': request.session.get('cart_data_obj', {}),
                   'totalcartitems': len(request.session.get('cart_data_obj', {})),
                   'cart_total_amount': cart_total_amount,
                   **context})

@login_required
def dashboard(request):
    return render(request, "core/account_dashboard.html")

def faq(request):
    return render(request, "core/faq.html")

def shipping_policy(request):
    return render(request, "core/shipping-policy.html")

@login_required
def orders(request):
    orders = CartOrder.objects.filter(user=request.user).order_by("-id")
    context = {
        "orders": orders
    }
    return render(request, "core/account_orders.html", context)

def order_detail(request, id):
    order = CartOrder.objects.filter(user=request.user, id=id)
    products = CartOrderItems.objects.filter(order=order)

    context = {
        "products": products,
    }
    return render(request, "core/order-detail.html", context)

@login_required
def address(request):
    return render(request, "core/account_address.html")

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

    # fetching rate without gst
    price_wo_gst = product_variant_types.first().varient_price if product_variant_types.exists() else product.price

    # Fetching GST rate
    if product_variant_types.exists():
        gst_rate = product_variant_types.first().gst_rate
    else:
        gst_rate = product.gst_rate

    # Calculating default price including GST
    if product_variant_types.exists():
        base_price = product_variant_types.first().varient_price
    else:
        base_price = product.price

    # Calculate GST amount
    gst_amount = base_price * Decimal(gst_rate.strip('%')) / 100

    # Calculate total price including GST and round off to two decimal places
    total_price = round(base_price + gst_amount, 2)

    default_packaging_size = product_variant_types.first().packaging_size if product_variant_types.exists() else product.packing_size

    product_images = ProductImages.objects.filter(product=product)

    context = {
        "products": product,
        "product_variants": product_variants,
        "product_variant_types": product_variant_types,
        "product_images": product_images,
        "default_price": total_price,
        "price_wo_gst": price_wo_gst,
        "default_packaging_size": default_packaging_size,
        "gst_rate": gst_rate,
    }

    return render(request, "core/product.html", context)

