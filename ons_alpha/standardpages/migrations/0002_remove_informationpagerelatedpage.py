from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("standardpages", "0001_initial"),
    ]

    operations = [
        migrations.DeleteModel(name="InformationPageRelatedPage"),
    ]
