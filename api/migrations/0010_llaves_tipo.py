# Generated manually: Add 'tipo' field to Llaves
from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('api', '0009_userprofile_active_provider_color'),
    ]

    operations = [
        migrations.AddField(
            model_name='llaves',
            name='tipo',
            field=models.CharField(choices=[('house', 'Casa'), ('car', 'Auto'), ('menga', 'Menga Canal')], default='house', max_length=10, db_index=True),
            preserve_default=False,
        ),
    ]
