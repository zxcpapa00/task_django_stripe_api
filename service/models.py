from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse


class Item(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('item_detail', args=[str(self.id)])


class StripeInfo(models.Model):
    item = models.OneToOneField('Item', on_delete=models.CASCADE)
    stripe_product_id = models.CharField(max_length=50, blank=True, null=True)
    stripe_price_id = models.CharField(max_length=50, blank=True, null=True)


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    items = models.ManyToManyField('Item', related_name='orders')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    stripe_payment_intent_id = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return f"Order {self.id}"

    def get_absolute_url(self):
        return reverse('order_detail', args=[str(self.id)])
