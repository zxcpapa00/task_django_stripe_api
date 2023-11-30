from django.conf import settings
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from service.models import Item, StripeInfo, OrderItem, Tax, Discount
import stripe

stripe.api_key = settings.STRIPE_SECRET_KEY


# Сигнал срабатывает при создании модели Item
@receiver(signal=post_save, sender=Item)
def create_product_in_stripe(sender, instance, created, **kwargs):
    if created:
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


@receiver(signal=post_delete, sender=OrderItem)
def delete_order_item(sender, instance, **kwargs):
    order = instance.order
    order.total_amount -= (instance.item.price * instance.quantity)
    order.save()


@receiver(post_save, sender=Tax)
def create_stripe_tax(sender, instance, created, **kwargs):
    if created:
        # Создание налога в Stripe
        stripe_tax = stripe.TaxRate.create(
            display_name=instance.name,
            description=instance.name,
            inclusive=False,
            percentage=instance.amount,
        )

        # Сохранение Stripe ID в модели
        instance.stripe_price_id = stripe_tax.id
        instance.save()


@receiver(post_save, sender=Discount)
def create_stripe_tax(sender, instance, created, **kwargs):
    if created:
        # Создание скидки в Stripe
        stripe_discount = stripe.Coupon.create(
            name=instance.name,
            percent_off=instance.amount,  # Процент скидки
            duration='forever',  # Продолжительность скидки
        )

        # Сохранение Stripe ID в модели
        instance.stripe_price_id = stripe_discount.id
        instance.save()
