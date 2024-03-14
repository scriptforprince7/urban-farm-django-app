from core.models import *

def default(request):
    main_categories = Main_category.objects.all()

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
