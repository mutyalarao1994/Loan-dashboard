import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('interest_app', '0005_dailyloan_dates_is_paid_seafood'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='dailyloan',
            name='end_date',
        ),
        migrations.AddField(
            model_name='dailyloan',
            name='paid_date',
            field=models.DateField(blank=True, null=True),
        ),
    ]
