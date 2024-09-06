# Generated by Django 4.2.16 on 2024-09-06 14:07

import django.db.models.deletion

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("wagtailcore", "0094_alter_page_locale"),
        ("auth", "0012_alter_user_first_name_max_length"),
        ("workflows", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="ReadyToPublishGroupTask",
            fields=[
                (
                    "task_ptr",
                    models.OneToOneField(
                        auto_created=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        serialize=False,
                        to="wagtailcore.task",
                    ),
                ),
                ("groups", models.ManyToManyField(to="auth.group")),
            ],
            options={
                "verbose_name": "Ready to publish Group approval task",
                "verbose_name_plural": "Ready to publish Group approval tasks",
            },
            bases=("wagtailcore.task",),
        ),
    ]