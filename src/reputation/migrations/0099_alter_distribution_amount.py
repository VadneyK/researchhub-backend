# Generated by Django 5.1.4 on 2025-01-02 22:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("reputation", "0098_deposit_network"),
    ]

    operations = [
        migrations.AlterField(
            model_name="distribution",
            name="amount",
            field=models.DecimalField(decimal_places=8, default=0, max_digits=19),
        ),
    ]
