from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('centers', '0032_culturalcenter_is_dxsh_project'),
    ]

    operations = [
        migrations.AddConstraint(
            model_name='culturalcenter',
            constraint=models.CheckConstraint(
                condition=models.Q(('is_featured', True), ('is_dxsh_project', True), _negated=True),
                name='center_not_both_featured_and_dxsh',
            ),
        ),
    ]
