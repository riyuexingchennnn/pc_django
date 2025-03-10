# Generated by Django 5.1.6 on 2025-02-11 08:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("qr_code", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="qrcodeid",
            name="state",
            field=models.CharField(
                default="unused", help_text="二维码使用情况", max_length=10
            ),
        ),
        migrations.AddField(
            model_name="temporarytoken",
            name="user",
            field=models.IntegerField(help_text="用户id", null=True),
        ),
    ]
