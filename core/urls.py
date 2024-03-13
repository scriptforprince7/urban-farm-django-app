from django.urls import include, path
from core.views import *

app_name = "core"

urlpatterns = [
    path("", index, name="index"),
    path("shop-category/", main_category, name="main_category"),
    path("category/<main_title>/", category, name="category"),
    path("product/<title>/", product_new, name="product_new"),
    path("add-to-cart/", add_to_cart, name="add-to-cart"),
    # path("product/<title>/", producttitle, name="producttitle"),
    path("search/", search_view, name="search"),
    path("delete-from-cart/", delete_item_from_cart, name="delete-from-cart"),
    path("update-cart/", update_cart, name="update-cart"),
    # path("checkout/", checkout_view, name="checkout"),
    path('paypal/', include('paypal.standard.ipn.urls')),
    path("payment-completed/", payment_completed_view, name="payment-completed"),
    path("payment-failed/", payment_failed_view, name="payment-failed"),
    path("about-us/", about, name="about-us"),
    path("contact-us/", contact, name="contact-us"),
    path("career", career, name="career"),
    path("blog/", blogs, name="blogs"),
    path("privacy-policy/", privacypolicy, name="privacypolicy"),
    path("cart/", cart, name="cart"),
    path("checkout/", checkout, name="checkout"),
    path("confirmation/", confirmation, name="confirmation"),
]
