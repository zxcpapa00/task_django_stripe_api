from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
import stripe
from django.views.decorators.csrf import csrf_exempt

from .models import Item, Order, OrderItem

stripe.api_key = settings.STRIPE_SECRET_KEY


@csrf_exempt
def get_checkout_session_id(request, item_id):
    try:
        item = Item.objects.get(pk=item_id)

        # Создаем сеанс оплаты в Stripe
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price': item.stripeinfo.stripe_price_id,
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
    order, created = Order.objects.get_or_create(user=request.user, stripe_payment_intent_id__isnull=True)

    order_item, create = OrderItem.objects.get_or_create(item_id=item_id, order=order)
    order.total_amount += order_item.item.price
    if order_item in order.order_items.all() and not create:
        order_item.quantity += 1
        order_item.save()
    else:
        order.order_items.add(order_item)
    order.save()
    return redirect('item_detail', item_id=item_id)


@login_required
def create_checkout_session(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)

    line_items = [{
        'price': order_item.item.stripeinfo.stripe_price_id,
        'quantity': order_item.quantity,
    } for order_item in order.order_items.all()]

    # Добавляем скидки
    discount = order.discounts.all()[0]
    discount_amount = int((discount.amount / 100) * order.total_amount)
    discount_item = {
        'price_data': {
            'currency': 'usd',
            'product_data': {
                'name': discount.name,
            },
            'unit_amount': -discount_amount,
        },
        'quantity': 1,
    }
    line_items.append(discount_item)

    # Добавляем сборы
    for tax in order.taxes.all():
        line_taxes = {
            'price_data': {
                'currency': 'usd',
                'product_data': {
                    'name': tax.name,
                },
                'unit_amount': int(tax.amount * 100),
            },
            'quantity': 1,
        }
        line_items.append(line_taxes)

    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=line_items,
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
