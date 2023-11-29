from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
import stripe
from django.views.decorators.csrf import csrf_exempt

from .models import Item, StripeInfo, Order

stripe.api_key = settings.STRIPE_SECRET_KEY


@csrf_exempt
def get_checkout_session_id(request, item_id):
    try:
        item = Item.objects.get(pk=item_id)

        # Получаем информацию о товаре и цене из модели StripeInfo
        stripe_info = StripeInfo.objects.get(item=item)
        price_id = stripe_info.stripe_price_id

        # Создаем сеанс оплаты в Stripe
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price': price_id,
                'quantity': 1,
            }],
            mode="payment",
            success_url=request.build_absolute_uri(item.get_absolute_url()),
            cancel_url=request.build_absolute_uri(item.get_absolute_url()),
        )

        return JsonResponse({'session_id': session.id})

    except Item.DoesNotExist:
        return JsonResponse({'error': 'Item not found'}, status=404)


def item_detail(request, item_id):
    item = Item.objects.get(pk=item_id)
    return render(request, 'item_detail.html', {'item': item})


@login_required
def add_to_cart(request, item_id):
    item = get_object_or_404(Item, id=item_id)
    order, created = Order.objects.get_or_create(user=request.user, stripe_payment_intent_id__isnull=True)
    if not order.total_amount:
        order.total_amount = item.price
    else:
        order.total_amount += item.price
    order.items.add(item)
    order.save()
    return redirect('item_detail', item_id=item_id)


@login_required
def create_checkout_session(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)

    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[{
            'price': item.stripeinfo.stripe_price_id,
            'quantity': 1,
        } for item in order.items.all()],
        mode='payment',
        success_url=request.build_absolute_uri(order.get_absolute_url()),
        cancel_url=request.build_absolute_uri(order.get_absolute_url()),
    )

    order.stripe_payment_intent_id = session.payment_intent
    order.save()

    return JsonResponse({'session_id': session.id})


@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'order_detail.html', {'order': order})
