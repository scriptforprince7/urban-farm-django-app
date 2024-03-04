from django.urls import include, path
from core.views import *

app_name = "core"

urlpatterns = [
    path("", index, name="index"),
    path("category/<cat_title>/", category, name="inner-category"),
    path("shop-category/", main_category, name="main_category"),
    path("category/", category, name="category"),
    path("product/", product_new, name="product_new"),
    path("add-to-cart/", add_to_cart, name="add-to-cart"),
    path("product/<slug:product_slug>/", product, name="product"),
    path("product/<title>/", producttitle, name="producttitle"),
    path("search/", search_view, name="search"),
    path("delete-from-cart/", delete_item_from_cart, name="delete-from-cart"),
    path("update-cart/", update_cart, name="update-cart"),
    path("checkout/", checkout_view, name="checkout"),
    path('paypal/', include('paypal.standard.ipn.urls')),
    path("payment-completed/", payment_completed_view, name="payment-completed"),
    path("payment-failed/", payment_failed_view, name="payment-failed"),
    path("about-us/", about, name="about-us"),
    path("contact-us/", contact, name="contact-us"),
    path("career", career, name="career"),
    path("blog/", blogs, name="blogs"),
    path("privacy-policy/", privacypolicy, name="privacypolicy"),
    path("<slug:sub_cat_slug>/", sub_category, name="sub-category"),
]
