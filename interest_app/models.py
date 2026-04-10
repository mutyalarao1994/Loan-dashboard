from django.db import models
from django.utils import timezone
from decimal import Decimal
from datetime import date, timedelta


class Loan(models.Model):
    name = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    monthly_interest_percent = models.DecimalField(
        max_digits=5, decimal_places=2, default=Decimal('2.00')
    )
    given_date = models.DateField(default=timezone.now)
    created_at = models.DateField(default=timezone.now)

    def month_day_difference(self):
        start = self.given_date
        end = timezone.now().date()
        if end < start:
            return 0, 0
        months = (end.year - start.year) * 12 + (end.month - start.month)
        if end.day < start.day:
            months -= 1
            prev_month_last_day = date(end.year, end.month, 1) - timezone.timedelta(days=1)
            days = prev_month_last_day.day - start.day + end.day
        else:
            days = end.day - start.day
        if days < 0:
            days = 0
        return months, days

    def month_day_text(self):
        months, days = self.month_day_difference()
        return f"{months} months {days} days"

    def monthly_interest_amount(self):
        return (self.amount * self.monthly_interest_percent) / Decimal('100')

    def total_monthly_interest_amount(self):
        months, days = self.month_day_difference()
        monthly_interest = self.monthly_interest_amount()
        daily_interest = monthly_interest / Decimal('30')
        return (
            (monthly_interest * Decimal(months)) +
            (daily_interest * Decimal(days))
        )

    def total_amount(self):
        return self.amount + self.total_monthly_interest_amount()

    def __str__(self):
        return self.name


class DailyLoan(models.Model):
    name = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    # Rate: rupees per 1000 per day (e.g. 1.5 means Rs.1.5 per Rs.1000 per day)
    daily_interest_rate = models.DecimalField(max_digits=7, decimal_places=3, default=Decimal('1.5'))
    start_date = models.DateField(default=timezone.now)
    is_paid = models.BooleanField(default=False)
    paid_date = models.DateField(null=True, blank=True)
    created_at = models.DateField(default=timezone.now)

    @property
    def effective_end_date(self):
        """Frozen on paid_date when paid; otherwise always today (keeps accruing)."""
        if self.is_paid and self.paid_date:
            return self.paid_date
        return date.today()

    @property
    def number_of_days(self):
        """Inclusive count: start_date to end_date, both days counted."""
        delta = self.effective_end_date - self.start_date
        return max(delta.days + 1, 1)

    def daily_interest_amount(self):
        """Daily interest = (principal / 1000) * rate"""
        return (self.amount / Decimal('1000')) * self.daily_interest_rate

    def total_interest(self):
        return self.daily_interest_amount() * Decimal(self.number_of_days)

    def total_amount(self):
        return self.amount + self.total_interest()

    def day_rows(self):
        """Return a list of dicts, one per day, for the breakdown table."""
        rows = []
        daily = self.daily_interest_amount()
        running_interest = Decimal('0')
        for day in range(1, self.number_of_days + 1):
            current_date = self.start_date + timedelta(days=day - 1)
            running_interest += daily
            rows.append({
                'day': day,
                'date': current_date,
                'principal': self.amount,
                'daily_interest': daily,
                'total_interest': running_interest,
                'total_amount': self.amount + running_interest,
            })
        return rows

    def __str__(self):
        return self.name


class SeaFood(models.Model):
    customer_name = models.CharField(max_length=100)
    prawn_count = models.PositiveIntegerField(default=0)
    kgs = models.DecimalField(max_digits=10, decimal_places=3)
    amount_paid = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0'))
    kg_per_commission = models.DecimalField(max_digits=8, decimal_places=2)
    is_payment_received = models.BooleanField(default=False)
    created_at = models.DateField(default=timezone.now)

    @property
    def total_commission(self):
        return self.kgs * self.kg_per_commission

    def __str__(self):
        return self.customer_name
