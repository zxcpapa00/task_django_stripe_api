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
