import datetime
from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('interest_app', '0004_dailyloan'),
    ]

    operations = [
        # ── DailyLoan field changes ──────────────────────────────────────
        migrations.AddField(
            model_name='dailyloan',
            name='start_date',
            field=models.DateField(default=datetime.date.today),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='dailyloan',
            name='end_date',
            field=models.DateField(default=datetime.date.today),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='dailyloan',
            name='is_paid',
            field=models.BooleanField(default=False),
        ),
        migrations.RemoveField(
            model_name='dailyloan',
            name='given_date',
        ),
        migrations.RemoveField(
            model_name='dailyloan',
            name='number_of_days',
        ),
        # ── New SeaFood model ────────────────────────────────────────────
        migrations.CreateModel(
            name='SeaFood',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('customer_name', models.CharField(max_length=100)),
                ('prawn_count', models.PositiveIntegerField(default=0)),
                ('kgs', models.DecimalField(decimal_places=3, max_digits=10)),
                ('amount_paid', models.DecimalField(decimal_places=2, default='0.00', max_digits=12)),
                ('kg_per_commission', models.DecimalField(decimal_places=2, max_digits=8)),
                ('is_payment_received', models.BooleanField(default=False)),
                ('created_at', models.DateField(default=django.utils.timezone.now)),
            ],
        ),
    ]
