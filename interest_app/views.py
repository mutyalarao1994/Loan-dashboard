from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from decimal import Decimal
from .models import Loan, DailyLoan, SeaFood


# ─────────────────────────────────────────────────────────────
# Context helpers
# ─────────────────────────────────────────────────────────────

def _monthly_summary(loans):
    total_amount = Decimal('0')
    monthly_interest = Decimal('0')
    total_monthly_interest = Decimal('0')
    for loan in loans:
        total_amount += loan.amount
        total_monthly_interest += loan.total_monthly_interest_amount()
        monthly_interest += loan.monthly_interest_amount()
    return total_amount, monthly_interest, total_monthly_interest, total_amount + total_monthly_interest


def _build_dashboard_context(extra=None):
    """Build the full context dict for the dashboard template."""
    loans = Loan.objects.all()
    total_amount, monthly_interest, total_monthly_interest, grand_total = _monthly_summary(loans)

    # Pending daily loans only (is_paid=False)
    pending_daily = DailyLoan.objects.filter(is_paid=False)
    d_pending_principal = Decimal('0')
    d_pending_daily_interest = Decimal('0')
    d_pending_interest = Decimal('0')
    for dl in pending_daily:
        d_pending_principal += dl.amount
        d_pending_daily_interest += dl.daily_interest_amount()
        d_pending_interest += dl.total_interest()

    # All daily loans total (for "total earned" section)
    d_all_total_interest = sum(
        (dl.total_interest() for dl in DailyLoan.objects.all()), Decimal('0')
    )

    # Pending seafoods (is_payment_received=False)
    sf_pending = SeaFood.objects.filter(is_payment_received=False)
    sf_pending_commission = sum((sf.total_commission for sf in sf_pending), Decimal('0'))
    sf_pending_amount_paid = sum((sf.amount_paid for sf in sf_pending), Decimal('0'))

    # All seafoods total commission
    sf_all_total_commission = sum(
        (sf.total_commission for sf in SeaFood.objects.all()), Decimal('0')
    )

    ctx = {
        'loans': loans,
        'total_amount': total_amount,
        'monthly_interest': monthly_interest,
        'total_monthly_interest': total_monthly_interest,
        'grand_total': grand_total,
        # Daily pending
        'pending_daily': pending_daily,
        'd_pending_principal': d_pending_principal,
        'd_pending_daily_interest': d_pending_daily_interest,
        'd_pending_interest': d_pending_interest,
        'd_pending_grand_total': d_pending_principal + d_pending_interest,
        # All-time totals
        'd_all_total_interest': d_all_total_interest,
        # Seafood pending
        'sf_pending': sf_pending,
        'sf_pending_commission': sf_pending_commission,
        'sf_pending_amount_paid': sf_pending_amount_paid,
        # Seafood all-time
        'sf_all_total_commission': sf_all_total_commission,
    }
    if extra:
        ctx.update(extra)
    return ctx


def _daily_calc_context(loans=None, edit_loan=None):
    if loans is None:
        loans = DailyLoan.objects.all()
    total_principal = Decimal('0')
    total_daily_interest = Decimal('0')
    total_interest = Decimal('0')
    for loan in loans:
        total_principal += loan.amount
        total_daily_interest += loan.daily_interest_amount()
        total_interest += loan.total_interest()
    ctx = {
        'loans': loans,
        'total_principal': total_principal,
        'total_daily_interest': total_daily_interest,
        'total_interest': total_interest,
        'grand_total': total_principal + total_interest,
    }
    if edit_loan:
        ctx['edit_loan'] = edit_loan
    return ctx


def _seafood_calc_context(records=None, edit_record=None):
    if records is None:
        records = SeaFood.objects.all()
    total_kgs = Decimal('0')
    total_amount_paid = Decimal('0')
    total_commission = Decimal('0')
    for sf in records:
        total_kgs += sf.kgs
        total_amount_paid += sf.amount_paid
        total_commission += sf.total_commission
    ctx = {
        'records': records,
        'total_kgs': total_kgs,
        'total_amount_paid': total_amount_paid,
        'total_commission': total_commission,
    }
    if edit_record:
        ctx['edit_record'] = edit_record
    return ctx


# ─────────────────────────────────────────────────────────────
# Monthly Loan Calculator views
# ─────────────────────────────────────────────────────────────

def index(request):
    return render(request, 'interest_app/index.html', _build_dashboard_context())


def monthly_loans(request):
    loans = Loan.objects.all()
    total_amount, monthly_interest, total_monthly_interest, grand_total = _monthly_summary(loans)
    return render(request, 'interest_app/monthly_loans.html', {
        'loans': loans,
        'total_amount': total_amount,
        'monthly_interest': monthly_interest,
        'total_monthly_interest': total_monthly_interest,
        'grand_total': grand_total,
    })


def add_loan(request):
    if request.method == "POST":
        Loan.objects.create(
            name=request.POST['name'],
            amount=request.POST['amount'],
            monthly_interest_percent=request.POST.get('monthly_interest_percent', 2),
            given_date=request.POST['given_date'],
            created_at=timezone.now().date(),
        )
    return redirect('monthly_loans')


def edit_loan(request, loan_id):
    loan = get_object_or_404(Loan, id=loan_id)
    if request.method == "POST":
        loan.name = request.POST['name']
        loan.amount = request.POST['amount']
        loan.monthly_interest_percent = request.POST.get('monthly_interest_percent', 2)
        loan.given_date = request.POST['given_date']
        loan.save()
        return redirect('monthly_loans')
    loans = Loan.objects.all()
    total_amount, monthly_interest, total_monthly_interest, grand_total = _monthly_summary(loans)
    return render(request, 'interest_app/monthly_loans.html', {
        'loans': loans,
        'edit_loan': loan,
        'total_amount': total_amount,
        'monthly_interest': monthly_interest,
        'total_monthly_interest': total_monthly_interest,
        'grand_total': grand_total,
    })


def delete_loan(request, loan_id):
    Loan.objects.filter(id=loan_id).delete()
    return redirect('monthly_loans')


# ─────────────────────────────────────────────────────────────
# Daily Loan Calculator views
# Formula: daily_interest = (principal / 1000) * rate
# ─────────────────────────────────────────────────────────────

def daily_loan_calculator(request):
    return render(request, 'interest_app/daily_loan_calculator.html', _daily_calc_context())


def add_daily_loan(request):
    if request.method == 'POST':
        DailyLoan.objects.create(
            name=request.POST['name'],
            amount=request.POST['amount'],
            daily_interest_rate=request.POST.get('daily_interest_rate', '1.5'),
            start_date=request.POST['start_date'],
            created_at=timezone.now().date(),
        )
    return redirect('daily_loan_calculator')


def edit_daily_loan(request, loan_id):
    loan = get_object_or_404(DailyLoan, id=loan_id)
    if request.method == 'POST':
        loan.name = request.POST['name']
        loan.amount = request.POST['amount']
        loan.daily_interest_rate = request.POST.get('daily_interest_rate', '1.5')
        loan.start_date = request.POST['start_date']
        loan.save()
        return redirect('daily_loan_calculator')
    loans = DailyLoan.objects.all()
    return render(request, 'interest_app/daily_loan_calculator.html', _daily_calc_context(loans, loan))


def delete_daily_loan(request, loan_id):
    DailyLoan.objects.filter(id=loan_id).delete()
    return redirect('daily_loan_calculator')


def toggle_daily_loan_paid(request, loan_id):
    loan = get_object_or_404(DailyLoan, id=loan_id)
    loan.is_paid = not loan.is_paid
    if loan.is_paid:
        # Freeze: record today as the final date for interest calculation
        loan.paid_date = timezone.now().date()
    else:
        # Unfreeze: clear paid_date so interest resumes accumulating from today
        loan.paid_date = None
    loan.save()
    return redirect('daily_loan_calculator')


# ─────────────────────────────────────────────────────────────
# Kushal Sea Foods views
# ─────────────────────────────────────────────────────────────

def seafoods(request):
    return render(request, 'interest_app/seafoods.html', _seafood_calc_context())


def add_seafood(request):
    if request.method == 'POST':
        SeaFood.objects.create(
            customer_name=request.POST['customer_name'],
            prawn_count=request.POST.get('prawn_count', 0),
            kgs=request.POST['kgs'],
            amount_paid=request.POST.get('amount_paid', '0'),
            kg_per_commission=request.POST['kg_per_commission'],
            created_at=timezone.now().date(),
        )
    return redirect('seafoods')


def edit_seafood(request, record_id):
    record = get_object_or_404(SeaFood, id=record_id)
    if request.method == 'POST':
        record.customer_name = request.POST['customer_name']
        record.prawn_count = request.POST.get('prawn_count', 0)
        record.kgs = request.POST['kgs']
        record.amount_paid = request.POST.get('amount_paid', '0')
        record.kg_per_commission = request.POST['kg_per_commission']
        record.save()
        return redirect('seafoods')
    records = SeaFood.objects.all()
    return render(request, 'interest_app/seafoods.html', _seafood_calc_context(records, record))


def delete_seafood(request, record_id):
    SeaFood.objects.filter(id=record_id).delete()
    return redirect('seafoods')


def toggle_seafood_payment(request, record_id):
    record = get_object_or_404(SeaFood, id=record_id)
    record.is_payment_received = not record.is_payment_received
    record.save()
    return redirect('seafoods')


# ─────────────────────────────────────────────────────────────
# Legacy download view (preserved)
# ─────────────────────────────────────────────────────────────

import json
import os
import pandas as pd

from django.conf import settings
from django.http import HttpResponse


def download_orders_json(request):
    excel_path = os.path.join(
        settings.BASE_DIR,
        "USPS Scale orders january 2026.xlsx",
    )

    df = pd.read_excel(excel_path)

    records = []
    for _, row in df.iterrows():
        records.append({
            "carrier": str(row.get("Carrier") or "").strip(),
            "internal_order_num": str(row.get("InternalOrderNbr") or "").strip(),
            "internal_shipment_num": str(row.get("InternalShipmentNbr") or "").strip(),
            "internal_container_num": str(row.get("InternalContainerNbr") or "").strip(),
            "erp_order_num": str(row.get("ERPOrder") or "").strip(),
            "customer_po": str(row.get("CustomerPO") or "").strip(),
            "tracking_number": str(row.get("TrackingNbr") or "").strip(),
        })

    data = json.dumps(records, indent=2)

    response = HttpResponse(data, content_type="application/json")
    response["Content-Disposition"] = 'attachment; filename="usps_scale_orders_jan_2026.json"'
    return response
