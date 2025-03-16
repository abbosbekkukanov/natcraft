# Generated by Django 5.1.3 on 2025-03-04 07:35


from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='product',
            name='latitude',
        ),
        migrations.RemoveField(
            model_name='product',
            name='longitude',
        ),
        migrations.AddField(
            model_name='product',
            name='discount',
            field=models.DecimalField(blank=True, decimal_places=2, help_text='Discount in percent', max_digits=5, null=True),
        ),
    ]
