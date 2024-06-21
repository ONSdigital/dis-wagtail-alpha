from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("inlineindex", "0001_initial"),
    ]

    operations = [
        migrations.DeleteModel(name="InlineIndexRelatedPage"),
    ]
