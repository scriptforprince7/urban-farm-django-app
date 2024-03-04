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

class ArchitectureImagesAdmin(admin.TabularInline):
    model = ArchitectureImages


class ProductVariantImagesAdmin(admin.StackedInline):
    model = ProductVariantImages
    extra = 0  # This allows adding multiple images at once in the admin

class ProductVarientAdmin(admin.StackedInline):
    model = ProductVarient
    extra = 0
    inlines = [ProductVariantImagesAdmin]

class SubCategoryImagesAdmin(admin.TabularInline):
    model = SubcategoryImages
    extra = 3  # This allows adding multiple images at once in the admin



class ProductAdmin(admin.ModelAdmin):
    inlines = [ProductImagesAdmin, ProductSeoAdmin, ProductVarientAdmin, ProductVariantImagesAdmin]
    list_display = ['company_name', 'main_category', 'category', 'sub_category', 'title', 'product_slug', 'price', 'featured', 'product_status']
    list_filter = ['company_name', 'main_category', 'category', 'sub_category', 'featured', 'product_status']  # Add fields you want to filter by
    search_fields = ['title', 'description']  # Add fields you want to search by

class ArchitectureAdmin(admin.ModelAdmin):
    inlines = [ArchitectureImagesAdmin]
    list_display = ['name', 'contact', 'email', 'address', 'description', 'instagram', 'facebook', 'linkedin', 'twitter', 'featured']
    list_filter = ['name', 'featured', 'contact', 'address', 'email']  # Add fields you want to filter by
    search_fields = ['title', 'description']  # Add fields you want to search by


class MainCategoryAdmin(admin.ModelAdmin):
    list_display = ['main_title', 'meta_description', 'meta_title', 'meta_tag', 'image', 'icon_img']     

class CategoryAdmin(admin.ModelAdmin):
    list_display = ['main_category', 'cat_title', 'meta_description', 'meta_title', 'meta_tag', 'image', 'big_image']
    list_filter = ['main_category']  # Fields to filter by

class CompanyNameAdmin(admin.ModelAdmin):
    list_display = ['maincat', 'category', 'sub_category', 'company_name_title', 'user', 'meta_description', 'meta_title', 'meta_tag', 'image', 'logo_img']
    list_filter = ['maincat', 'category', 'sub_category']  # Add fields you want to filter by
    search_fields = ['company_name_title', 'meta_description', 'meta_title', 'meta_tag']


class SubCategoryAdmin(admin.ModelAdmin):
    inlines = [SubCategoryImagesAdmin]
    list_display = ['maincat', 'category', 'sub_cat_title', 'slug', 'user', 'page_about_description', 'youtube_link', 'image']
    list_filter = ['maincat', 'category']  # Add fields you want to filter by
    search_fields = ['sub_cat_title', 'meta_description', 'meta_title']

class CartOrderAdmin(admin.ModelAdmin):
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
admin.site.register(Architecture, ArchitectureAdmin)
admin.site.register(Main_category, MainCategoryAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Company_name, CompanyNameAdmin)
admin.site.register(Sub_categories, SubCategoryAdmin)
admin.site.register(CartOrder, CartOrderAdmin)
admin.site.register(CartOrderItems, CartOrderItemsAdmin)
admin.site.register(ProductReview, ProductReviewAdmin)
admin.site.register(Wishlist, wishlistAdmin)
admin.site.register(Address, AddressAdmin)
admin.site.register(PrivacyPolicy, PrivacyPolicyAdmin)
admin.site.register(Blogs, BlogsAdmin)

    


