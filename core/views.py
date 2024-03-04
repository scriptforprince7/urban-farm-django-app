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


def index(request):
    product = Main_category.objects.all()

    context = {
        "main_cat":product,
    }
    return render(request, 'core/index.html', context)

def category(request):
    return render(request, "core/category.html")

def sub_category(request, sub_cat_slug):
    sub_cats = Sub_categories.objects.filter(slug=sub_cat_slug)

    if not sub_cats.exists():
        # Handle the case where no objects are found
        raise Http404("Sub-category does not exist")

    sub_cat = sub_cats.first()

    related_sub_categories = Sub_categories.objects.filter(maincat=sub_cat.maincat, category=sub_cat.category)
    company_names = Company_name.objects.filter(sub_category=sub_cat)
    
    # Create a dictionary to store company names and their associated products
    company_products = {}
    for company in company_names:
        products = Product.objects.filter(company_name=company)
        company_products[company] = products

    # Fetch sub-categories images
    sub_cat_images = SubcategoryImages.objects.filter(sub_category=sub_cat)
    image_urls = [image.images.url for image in sub_cat_images]

    context = {
        "sub_cat": sub_cat,
        "company_products": company_products,
        "related_sub_categories": related_sub_categories,
        "sub_cat_images": sub_cat_images,
        "image_urls": image_urls,
    }

    return render(request, "core/sub-category.html", context)

def main_category(request):
    return render(request, "core/main_category.html")


def add_to_cart(request):
    cart_product = {}
    cart_product[str(request.GET['id'])] = {
        'title': request.GET['title'],
        'qty': request.GET['qty'],
        'price': request.GET['price'],
        'image': request.GET['image'],
        'pid': request.GET['pid'],
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
            price_str = item['price'].replace('₹', '').replace(',', '').strip()
            price = float(price_str)
            cart_total_amount += int(item['qty']) * price

        return render(request, "core/cart.html", {"cart_data": request.session['cart_data_obj'], 'totalcartitems': len(request.session['cart_data_obj']), 'cart_total_amount': cart_total_amount})
    else:
        messages.warning(request, "Your cart is empty")
        return redirect("core:index")


def product(request, product_slug):
    products = Product.objects.filter(product_slug=product_slug)

    if not products.exists():
        # Handle the case where no objects are found
        raise Http404("Product does not exist")

    # If there are multiple objects, you may want to choose one or handle the situation appropriately
    main_product = products.first()

    related_products = Product.objects.filter(company_name=main_product.company_name).exclude(pk=main_product.pk)[:10]
    product_images = ProductImages.objects.filter(product=main_product)
    product_varients = ProductVarient.objects.filter(product=main_product)
    related_company = main_product.company_name
    related_subcategory = main_product.sub_category

    context = {
        "main_product": main_product,
        "related_products": related_products,
        "product_images": product_images,
        "related_company": related_company,
        "related_subcategory": related_subcategory,
        "product_varients" : product_varients,
    }
    return render(request, "core/product.html", context)

def producttitle(request, title):
    products = Product.objects.filter(title=title)

    if not products.exists():
        # Handle the case where no objects are found
        raise Http404("Product does not exist")

    # If there are multiple objects, you may want to choose one or handle the situation appropriately
    main_product = products.first()

    related_products = Product.objects.filter(company_name=main_product.company_name).exclude(pk=main_product.pk)[:10]
    product_images = ProductImages.objects.filter(product=main_product)
    product_varients = ProductVarient.objects.filter(product=main_product)
    related_company = main_product.company_name
    related_subcategory = main_product.sub_category

    context = {
        "main_product": main_product,
        "related_products": related_products,
        "product_images": product_images,
        "related_company": related_company,
        "related_subcategory": related_subcategory,
        "product_varients" : product_varients,
    }
    return render(request, "core/product.html", context)


def search_view(request):
    query = request.GET.get("q")

    products = Product.objects.filter(title__icontains=query).order_by("-date")

    context = {
        "products": products,
        "query": query,
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


    context = render_to_string("core/cart.html", {"cart_data": request.session['cart_data_obj'], 'totalcartitems': len(request.session['cart_data_obj']), 'cart_total_amount': cart_total_amount})
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


    context = render_to_string("core/cart.html", {"cart_data": request.session['cart_data_obj'], 'totalcartitems': len(request.session['cart_data_obj']), 'cart_total_amount': cart_total_amount})
    return JsonResponse({"data": context, 'totalcartitems': len(request.session['cart_data_obj'])}) 



@login_required
def checkout_view(request):
    host = request.get_host()
    paypal_dict = {
        'business' : settings.PAYPAL_RECEIVER_EMAIL,
        'amount' : '200',
        'item_name' : "Order-item No. 3",
        'invoice' : "INVOICE_NO_3",
        'currency_code' : "INR",
        'notify_url' : 'http://{}{}'.format(host, reverse('core:paypal-ipn')),
        'return_url' : 'http://{}{}'.format(host, reverse('core:payment-completed')),
        'cancel_url' : 'http://{}{}'.format(host, reverse('core:payment-failed')),
    }

    paypal_payment_button = PayPalPaymentsForm(initial=paypal_dict)
     
    cart_total_amount = 0
    if 'cart_data_obj' in request.session:
        for p_id, item in request.session['cart_data_obj'].items():
            cart_total_amount += int(item['qty']) * float(item['price'])

    return render(request, "core/checkout.html", {"cart_data": request.session['cart_data_obj'], 'totalcartitems': len(request.session['cart_data_obj']), 'cart_total_amount': cart_total_amount, 'paypal_payment_button': paypal_payment_button})

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


def com_name(request):
    return render(request, "core/sub-category.html")

def arch(request):
    architectures = Architecture.objects.filter(featured=True)
    architecture = Architecture.objects.filter(featured=False)
    archi = Architecture.objects.all()

    context = {
        "architectures": architectures,
        "architecture": architecture,
        "archi": archi,

    }
    return render(request, "arch/index.html", context)

def arch_name(request, name):
    architecture = get_object_or_404(Architecture, name=name)
    arch_images = ArchitectureImages.objects.filter(architecture=architecture)

    context = {
        "architecture": architecture,
        "arch_images": arch_images,
    }
    return render(request, "arch/portfolio-details.html", context)

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
    
def product_new(request):
    return render(request, "core/product.html")





        
    





