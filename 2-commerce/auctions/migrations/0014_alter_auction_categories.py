# Generated by Django 3.2.9 on 2021-11-27 23:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0013_alter_comment_auction'),
    ]

    operations = [
        migrations.AlterField(
            model_name='auction',
            name='categories',
            field=models.ManyToManyField(related_name='listings', to='auctions.Category'),
        ),
    ]
