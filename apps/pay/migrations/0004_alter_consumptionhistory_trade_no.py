# Generated by Django 5.1.4 on 2025-02-08 05:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("pay", "0003_remove_consumptionhistory_created_time_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="consumptionhistory",
            name="trade_no",
            field=models.UUIDField(
                help_text="订单号", primary_key=True, serialize=False
            ),
        ),
    ]
