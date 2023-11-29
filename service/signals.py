from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

from service.models import Item, StripeInfo


# Сигнал срабатывает при создании модели Item
@receiver(signal=post_save, sender=Item)
def create_product_in_stripe(sender, instance, created, **kwargs):
    if created:
        import stripe
        stripe.api_key = settings.STRIPE_SECRET_KEY

        # Создаём товар в Stripe
        product = stripe.Product.create(
            name=instance.name,
            description=instance.description,
            type='good',
        )
        price = stripe.Price.create(
            product=product.id,
            unit_amount=int(instance.price * 100),
            currency='usd',
        )

        # Передаём price_id и product_id
        stripe_info = StripeInfo.objects.create(item=instance, stripe_product_id=product.id, stripe_price_id=price.id)
