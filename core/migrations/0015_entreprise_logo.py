# Generated manually for logo field

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0014_emailverification'),
    ]

    operations = [
        migrations.AddField(
            model_name='entreprise',
            name='logo',
            field=models.ImageField(blank=True, help_text="Logo de l'entreprise", null=True, upload_to='entreprises/logos/'),
        ),
    ]






