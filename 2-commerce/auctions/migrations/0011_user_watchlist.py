# Generated by Django 3.2.9 on 2021-11-23 22:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0010_auto_20211122_2217'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='watchlist',
            field=models.ManyToManyField(related_name='listings', to='auctions.Auction'),
        ),
    ]
