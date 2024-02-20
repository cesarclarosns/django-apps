from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.deletion import CASCADE
from django.db.models.enums import Choices
from djmoney.models.fields import MoneyField
from django.utils import timezone


class Auction(models.Model):
    categories = models.ManyToManyField('Category')
    description = models.CharField(max_length=200)
    image_url = models.URLField(
        default="https://www.sinrumbofijo.com/wp-content/uploads/2016/05/default-placeholder.png")
    pub_date = models.DateTimeField(default=timezone.now)
    state = models.BooleanField(default=True)
    title = models.CharField(max_length=30)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=CASCADE, null=True, related_name='owner')

    def __str__(self):
        return self.title
    
    def current_bid(self):
        return self.bids.order_by('-amount')[0]
    
    def starting_bid(self):
        return self.bids.order_by('amount')[0]

    def bids_number(self):
        if self.bids.count() == 0:
            return 0
        if self.bids.count() == 1:
            return 1
        return 2
    
    
class Bid(models.Model):
    auction = models.ForeignKey('Auction', on_delete=CASCADE, null=True, related_name='bids')
    amount = MoneyField(max_digits=10, decimal_places=2)
    pub_date = models.DateTimeField(default=timezone.now)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=CASCADE, null=True)
    
    def __str__(self):
        return '%s %s' % (self.amount, self.amount_currency)
    
    
class Category(models.Model):
    category = models.CharField(max_length=30)

    def __str__(self):
        return self.category


class Comment(models.Model):
    auction = models.ForeignKey('Auction', on_delete=CASCADE, null=True, related_name="comments")
    comment = models.CharField(max_length=300)
    pub_date = models.DateTimeField(default=timezone.now)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=CASCADE, null=True)

    def __str__(self):
        return self.comment
    

class User(AbstractUser):
    watchlist = models.ManyToManyField('Auction', related_name='listings')
    
    def __str__(self):
        return self.username
