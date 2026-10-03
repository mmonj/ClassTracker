from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('class_tracker', '0055_alter_coursesection_unique_together_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='course',
            old_name='code',
            new_name='prefix',
        ),
        migrations.AlterField(
            model_name='course',
            name='prefix',
            field=models.CharField(default='', max_length=100, verbose_name='Course Prefix'),
        ),
    ]
