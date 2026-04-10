from django.urls import path
from . import views

urlpatterns = [
    # ── Dashboard ─────────────────────────────────────────────
    path('', views.index, name='index'),

    # ── Monthly Loan Calculator ────────────────────────────────
    path('monthly-loans/', views.monthly_loans, name='monthly_loans'),
    path('monthly-loans/add/', views.add_loan, name='add_loan'),
    path('monthly-loans/edit/<int:loan_id>/', views.edit_loan, name='edit_loan'),
    path('monthly-loans/delete/<int:loan_id>/', views.delete_loan, name='delete_loan'),
    path('download/', views.download_orders_json),

    # ── Daily Loan Calculator ──────────────────────────────────
    path('daily-loan-calculator/', views.daily_loan_calculator, name='daily_loan_calculator'),
    path('daily-loan-calculator/add/', views.add_daily_loan, name='add_daily_loan'),
    path('daily-loan-calculator/edit/<int:loan_id>/', views.edit_daily_loan, name='edit_daily_loan'),
    path('daily-loan-calculator/delete/<int:loan_id>/', views.delete_daily_loan, name='delete_daily_loan'),
    path('daily-loan-calculator/toggle/<int:loan_id>/', views.toggle_daily_loan_paid, name='toggle_daily_loan_paid'),

    # ── Kushal Sea Foods ───────────────────────────────────────
    path('seafoods/', views.seafoods, name='seafoods'),
    path('seafoods/add/', views.add_seafood, name='add_seafood'),
    path('seafoods/edit/<int:record_id>/', views.edit_seafood, name='edit_seafood'),
    path('seafoods/delete/<int:record_id>/', views.delete_seafood, name='delete_seafood'),
    path('seafoods/toggle/<int:record_id>/', views.toggle_seafood_payment, name='toggle_seafood_payment'),
]
