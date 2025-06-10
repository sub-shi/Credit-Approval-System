from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from datetime import date, timedelta
from rest_framework import status
from core.models import Customer, Loan
from core.serializers import RegisterCustomerSerializer, CheckEligibilitySerializer, LoanSummarySerializer, ViewLoanSerializer
from core.utils import calculate_credit_score



#REGISTER API

class RegisterCustomerView(APIView):
    def post(self, request):
        serializer = RegisterCustomerSerializer(data=request.data)
        if serializer.is_valid():
            customer = serializer.save()
            return Response({
                'customer_id': customer.id,
                'approved_limit': customer.approved_limit
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

    
#CHECK ELIGIBILITY API

class CheckEligibilityView(APIView):
    def post(self, request):
        serializer = CheckEligibilitySerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        customer_id = serializer.validated_data['customer_id']
        loan_amount = serializer.validated_data['loan_amount']
        interest_rate = serializer.validated_data['interest_rate']
        tenure = serializer.validated_data['tenure']

        try:
            customer = Customer.objects.get(id=customer_id)
        except Customer.DoesNotExist:
            return Response({'error': 'Customer not found.'}, status=status.HTTP_404_NOT_FOUND)

        credit_score, current_loans_sum = calculate_credit_score(customer)

        # APPROVAL LOGIC
        approval = False
        corrected_interest_rate = interest_rate

        if credit_score > 50:
            approval = True
        elif 30 < credit_score <= 50:
            if interest_rate > 12:
                approval = True
            else:
                corrected_interest_rate = 16
                approval = True
        elif 10 < credit_score <= 30:
            if interest_rate > 16:
                approval = True
            else:
                corrected_interest_rate = 20
                approval = True
        else:
            approval = False

        # EMI CONSTRAINT
        monthly_installment = loan_amount * (corrected_interest_rate / 100) / tenure
        if current_loans_sum > (0.5 * customer.monthly_salary):
            approval = False

        response_data = {
            'customer_id': customer_id,
            'approval': approval,
            'interest_rate': interest_rate,
            'corrected_interest_rate': corrected_interest_rate if corrected_interest_rate != interest_rate else None,
            'tenure': tenure,
            'monthly_installment': monthly_installment,
            'credit_score': credit_score
        }

        return Response(response_data, status=status.HTTP_200_OK)
    


# CREATE LOAN API

class CreateLoanView(APIView):
    def post(self, request):
        data = request.data

        customer_id = data.get('customer_id')
        loan_amount = data.get('loan_amount')
        interest_rate = data.get('interest_rate')
        tenure = data.get('tenure')

        if not all([customer_id, loan_amount, interest_rate, tenure]):
            return Response({'error': 'Missing required fields.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            customer = Customer.objects.get(id=customer_id)
        except Customer.DoesNotExist:
            return Response({'error': 'Customer not found.'}, status=status.HTTP_404_NOT_FOUND)

        # CALCULATE CREDIT SCORE & CURRENT LOANS
        credit_score, current_loans_sum = calculate_credit_score(customer)

        # APPROVAL LOGIC
        approval = False
        corrected_interest_rate = interest_rate

        if credit_score > 50:
            approval = True
        elif 30 < credit_score <= 50:
            if interest_rate > 12:
                approval = True
            else:
                corrected_interest_rate = 16
                approval = True
        elif 10 < credit_score <= 30:
            if interest_rate > 16:
                approval = True
            else:
                corrected_interest_rate = 20
                approval = True
        else:
            approval = False

        # EMI CONSTRAINT:
        if current_loans_sum > (0.5 * customer.monthly_salary):
            approval = False

        # MONTHLY INSTALLMENT FORMULA
        monthly_installment = loan_amount * (corrected_interest_rate / 100) / tenure

        if approval:
            today = date.today()
            end_date = today + timedelta(days=tenure * 30)

            loan = Loan.objects.create(
                customer=customer,
                loan_amount=loan_amount,
                tenure=tenure,
                interest_rate=corrected_interest_rate,
                monthly_repayment=monthly_installment,
                emis_paid_on_time=0,
                start_date=today,
                end_date=end_date
            )

            response_data = {
                'loan_id': loan.id,
                'customer_id': customer_id,
                'loan_approved': True,
                'message': 'Loan approved!',
                'monthly_installment': monthly_installment
            }
        else:
            response_data = {
                'loan_id': None,
                'customer_id': customer_id,
                'loan_approved': False,
                'message': 'Loan not approved due to eligibility criteria.',
                'monthly_installment': 0
            }

        return Response(response_data, status=status.HTTP_200_OK)
    

    
# VIEW LOAN DETAILS API

class ViewLoanDetailsView(APIView):
    def get(self, request, loan_id):
        loan = get_object_or_404(Loan.objects.select_related('customer'), id=loan_id)

        serializer = ViewLoanSerializer(loan)

        return Response(serializer.data, status=status.HTTP_200_OK)
    
    
    
# VIEW CUSTOMER LOANS API

class ViewCustomerLoansView(APIView):
    def get(self, request, customer_id):
        try:
            customer = Customer.objects.get(id=customer_id)
        except Customer.DoesNotExist:
            return Response({'error': 'Customer not found.'}, status=status.HTTP_404_NOT_FOUND)

        customer_loans = Loan.objects.filter(customer=customer)

        serializer = LoanSummarySerializer(customer_loans, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
