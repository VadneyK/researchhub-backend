# Generated by Django 2.2 on 2022-02-10 21:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0076_auto_20220209_2315'),
    ]

    operations = [
        migrations.AlterField(
            model_name='gatekeeper',
            name='type',
            field=models.CharField(choices=[('EDITOR_PAYOUT_ADMIN', 'EDITOR_PAYOUT_ADMIN'), ('ELN', 'ELN'), ('CLIENT_PERMISSIONS', 'CLIENT_PERMISSIONS'), ('PAYOUT_EXCLUSION', 'PAYOUT_EXCLUSION')], db_index=True, max_length=128),
        ),
    ]
