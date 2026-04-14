from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('centers', '0031_guesthouse'),
    ]

    operations = [
        migrations.AddField(
            model_name='culturalcenter',
            name='is_dxsh_project',
            field=models.BooleanField(default=False, verbose_name='DXSh loyiha'),
        ),
    ]
