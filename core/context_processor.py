from core.models import *

def default(request):
    main_categories = Main_category.objects.filter(active_status='published')

    halfway_index = len(main_categories) // 2

    first_half_categories = main_categories[:halfway_index]
    second_half_categories = main_categories[halfway_index:]

    return {
        "main_cat": main_categories,
        'first_half_categories': first_half_categories,
        'second_half_categories': second_half_categories,
    }


def defaultOne(request):
    products = Product.objects.all()

    return {
        "products_count": products,
    }

def cart_context(request):
    cart_total_amount = 0
    total_cart_items = 0
    cart_data = {}

    if 'cart_data_obj' in request.session:
        cart_data = request.session['cart_data_obj']

        for p_id, item in cart_data.items():
            cart_total_amount += int(item['qty']) * float(item['price'])
            total_cart_items += int(item['qty'])

    return {
        'cart_total_amount': cart_total_amount,
        'total_cart_items': total_cart_items,
        'cart_data': cart_data  # Include cart_data in the context
    }



