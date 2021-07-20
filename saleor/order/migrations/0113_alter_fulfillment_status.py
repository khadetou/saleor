# Generated by Django 3.2.5 on 2021-07-19 09:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("order", "0112_auto_20210616_0548"),
    ]

    operations = [
        migrations.AlterField(
            model_name="fulfillment",
            name="status",
            field=models.CharField(
                choices=[
                    ("fulfilled", "Fulfilled"),
                    ("refunded", "Refunded"),
                    ("returned", "Returned"),
                    ("replaced", "Replaced"),
                    ("refunded_and_returned", "Refunded and returned"),
                    ("canceled", "Canceled"),
                    ("waiting_for_acceptance", "Waiting for acceptance"),
                ],
                default="fulfilled",
                max_length=32,
            ),
        ),
    ]
