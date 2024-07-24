# Generated by Django 4.2.14 on 2024-07-24 12:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("user", "0119_userverification"),
    ]

    operations = [
        migrations.AlterField(
            model_name="userverification",
            name="status",
            field=models.TextField(
                choices=[
                    ("APPROVED", "Approved"),
                    ("DECLINED", "Declined"),
                    ("FAILED", "Failed"),
                    ("PENDING", "Pending"),
                ]
            ),
        ),
    ]
