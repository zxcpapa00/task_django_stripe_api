from django.urls import path
from .views import get_checkout_session_id, item_detail, add_to_cart, create_checkout_session, order_detail

urlpatterns = [
    path('buy/<int:item_id>/', get_checkout_session_id, name='get_checkout_session_id'),
    path('item/<int:item_id>/', item_detail, name='item_detail'),
    path('add_to_cart/<int:item_id>/', add_to_cart, name='add_to_cart'),
    path('order_detail/<int:order_id>/', order_detail, name='order_detail'),
    path('order_buy/<int:order_id>/', create_checkout_session, name='create_checkout_session'),
]
