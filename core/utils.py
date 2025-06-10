# core/utils.py

from datetime import date
from django.db.models import Sum
from .models import Loan

def calculate_credit_score(customer):
    customer_loans = Loan.objects.filter(customer=customer)

    #  PAST LOANS PAID ON TIME → COMPARE EACH LOAN EMIS_PAID_ON_TIME >= LOAN.TENURE
    loans_paid_on_time = sum(1 for loan in customer_loans if loan.emis_paid_on_time >= loan.tenure)

    #  NUMBER OF LOANS TAKEN IN PAST
    total_loans_taken = customer_loans.count()

    #  LOAN ACTIVITY IN CURRENT YEAR
    current_year = date.today().year
    loans_this_year = customer_loans.filter(start_date__year=current_year).count()

    #  LOAN APPROVED VOLUME
    loan_volume = customer_loans.aggregate(total_amount=Sum('loan_amount'))['total_amount'] or 0

    #  SUM OF CURRENT LOANS (ACTIVE LOANS)
    today = date.today()
    active_loans = customer_loans.filter(end_date__gte=today)
    current_loans_sum = sum(loan.monthly_repayment for loan in active_loans)

    # IF SUM OF CURRENT LOANS > APPROVED LIMIT → CREDIT SCORE = 0
    if current_loans_sum > customer.approved_limit:
        credit_score = 0
    else:
        credit_score = (
            (loans_paid_on_time * 25) +
            (total_loans_taken * 10) +
            (loans_this_year * 10) +
            (loan_volume / 100000)
        )
        credit_score = min(credit_score, 100)

    return credit_score, current_loans_sum

