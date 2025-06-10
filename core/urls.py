from django.urls import path
from core.views import RegisterCustomerView, CheckEligibilityView, CreateLoanView, ViewLoanDetailsView, ViewCustomerLoansView

urlpatterns = [
    path('register/', RegisterCustomerView.as_view(), name='register'),
    path('check-eligibility/', CheckEligibilityView.as_view(), name='check-eligibility'),
    path('create-loan/', CreateLoanView.as_view(), name='create-loan'),
    path('view-loan/<int:loan_id>/', ViewLoanDetailsView.as_view(), name='view-loan-details'),
    path('view-loans/<int:customer_id>/', ViewCustomerLoansView.as_view(), name='view-loans'),
]
