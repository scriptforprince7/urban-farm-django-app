from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from .models import *

class MainCategorySitemap(Sitemap):
    changefreq = 'weekly'
    priority = 0.9

    def items(self):
        return Main_category.objects.all()

    def location(self, obj):
        return reverse('core:main_category', kwargs={'main_title': str(obj.main_title)})

class CategorySitemap(Sitemap):
    changefreq = 'weekly'
    priority = 0.8

    def items(self):
        return Category.objects.all()

    def location(self, obj):
        return reverse('core:inner-category', kwargs={'cat_title': str(obj.cat_title)})

class SubCategorySitemap(Sitemap):
    changefreq = 'weekly'
    priority = 0.7

    def items(self):
        return Sub_categories.objects.all()

    def location(self, obj):
        return reverse('core:sub-category', kwargs={'sub_cat_slug': str(obj.slug)})

class ProductSitemap(Sitemap):
    changefreq = 'weekly'
    priority = 0.6

    def items(self):
        return Product.objects.all()

    def location(self, obj):
        return reverse('core:product', kwargs={'product_slug': str(obj.id)})  # or 'code' if that's the unique field



