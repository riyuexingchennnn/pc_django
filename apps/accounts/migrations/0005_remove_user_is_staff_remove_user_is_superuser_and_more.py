# Generated by Django 5.1.4 on 2025-01-26 16:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0004_rename_vertification_code_user_verification_code"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="user",
            name="is_staff",
        ),
        migrations.RemoveField(
            model_name="user",
            name="is_superuser",
        ),
        migrations.RemoveField(
            model_name="user",
            name="left_space",
        ),
        migrations.AddField(
            model_name="user",
            name="used_space",
            field=models.IntegerField(default=1024, verbose_name="已用空间"),
        ),
        migrations.AlterField(
            model_name="user",
            name="avatar",
            field=models.ImageField(
                blank=True,
                default="avatar/default.png",
                null=True,
                upload_to="avatars/",
                verbose_name="头像",
            ),
        ),
        migrations.AlterField(
            model_name="user",
            name="is_active",
            field=models.BooleanField(default=True, verbose_name="是否在线"),
        ),
    ]
