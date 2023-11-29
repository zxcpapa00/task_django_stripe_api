from django.conf import settings
from django.shortcuts import render
from django.http import JsonResponse
import stripe
from django.views.decorators.csrf import csrf_exempt

from .models import Item, StripeInfo

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
