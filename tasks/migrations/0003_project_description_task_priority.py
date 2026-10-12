from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('tasks', '0002_grouppeople_project_group'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='description',
            field=models.TextField(blank=True, default='', verbose_name='Описание'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='task',
            name='priority',
            field=models.CharField(
                choices=[('low', 'Низкий'), ('medium', 'Средний'), ('high', 'Высокий')],
                default='medium',
                max_length=10,
                verbose_name='Приоритет',
            ),
        ),
    ]
