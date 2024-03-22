from django.contrib import admin
from core.models import *

class ProductSeoAdmin(admin.StackedInline):
    model = ProductSeo
    extra = 0
    fields = (
        'canonical_link',
        'meta_description',
        'meta_title',
        'meta_tag',
        'meta_robots',
        'og_url',
        'og_title',
        'og_description',
        'og_image',
        'twitter_title',
        'twitter_description',
    )

class ProductImagesAdmin(admin.TabularInline):
    model = ProductImages
    extra = 0

class ProductVariantImagesAdmin(admin.StackedInline):
    model = ProductVariantTypes
    extra = 0  # This allows adding multiple images at once in the admin

class ProductVarientAdmin(admin.StackedInline):
    model = ProductVarient
    extra = 0
    inlines = [ProductVariantImagesAdmin]

class ProductAdmin(admin.ModelAdmin):
    inlines = [ProductImagesAdmin, ProductSeoAdmin, ProductVarientAdmin, ProductVariantImagesAdmin]
    list_display = ['main_category','title', 'product_slug', 'packing_size', 'price', 'product_status']
    list_filter = ['main_category', 'category', 'featured', 'product_status'] 
    search_fields = ['title', 'description'] 

class MainCategoryAdmin(admin.ModelAdmin):
    list_display = ['main_title', 'image', 'description', 'banner_image']     

class CategoryAdmin(admin.ModelAdmin):
    list_display = ['main_category', 'cat_title', 'meta_description', 'meta_title', 'meta_tag', 'image', 'big_image']
    list_filter = ['main_category']  # Fields to filter by

class CartOrderAdmin(admin.ModelAdmin):
    list_editable = ['paid_status', 'product_status']
    list_display = ['user', 'price', 'paid_status', 'order_date', 'product_status']

class CartOrderItemsAdmin(admin.ModelAdmin):
    list_display = ['order', 'invoice_no', 'item', 'image', 'qty', 'price', 'total']

class ProductReviewAdmin(admin.ModelAdmin):
    list_display = ['user', 'product', 'review', 'rating'] 

class wishlistAdmin(admin.ModelAdmin):
    list_display = ['user', 'product', 'date']

class AddressAdmin(admin.ModelAdmin):
    list_display = ['user', 'address', 'status']   

class PrivacyPolicyAdmin(admin.ModelAdmin):
    list_display = ['privacy_policy_content']     

class BlogsAdmin(admin.ModelAdmin):
    list_display = ['blog_title', 'blog_image', 'blog_description', 'blog_tags']      

admin.site.register(Product, ProductAdmin)
admin.site.register(Main_category, MainCategoryAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(CartOrder, CartOrderAdmin)
admin.site.register(CartOrderItems, CartOrderItemsAdmin)
admin.site.register(ProductReview, ProductReviewAdmin)
admin.site.register(Wishlist, wishlistAdmin)
admin.site.register(Address, AddressAdmin)
admin.site.register(PrivacyPolicy, PrivacyPolicyAdmin)
admin.site.register(Blogs, BlogsAdmin)

