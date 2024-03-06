from core.models import *

def default(request):
    main_category = Main_category.objects.all()

    return {
        'main_cat': main_category,
    }

