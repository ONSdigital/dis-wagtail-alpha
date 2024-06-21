from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("events", "0001_initial"),
    ]

    operations = [
        migrations.DeleteModel(name="EventPageRelatedPage"),
    ]
