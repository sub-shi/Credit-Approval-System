from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from core.models import Customer, Loan

class APITestCase(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.customer = Customer.objects.create(
            first_name="Test",
            last_name="User",
            age=21,
            phone_number=8093707370,
            monthly_salary=50000,
            approved_limit=1800000
        )

    def test_register_customer(self):
        url = reverse('register')
        data = {
            "first_name": "Ana",
            "last_name": "Mesa",
            "age": 25,
            "monthly_income": 40000,
            "phone_number": "9953004088",
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('customer_id', response.data)
        self.assertIn('approved_limit', response.data)

    def test_check_eligibility(self):
        url = reverse('check-eligibility')
        data = {
            "customer_id": self.customer.id,
            "loan_amount": 100000,
            "interest_rate": 12,
            "tenure": 12
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('approval', response.data)
        self.assertIn('monthly_installment', response.data)

    def test_create_loan(self):
        url = reverse('create-loan')
        data = {
            "customer_id": self.customer.id,
            "loan_amount": 100000,
            "interest_rate": 12,
            "tenure": 12
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('loan_id', response.data)
        self.assertIn('loan_approved', response.data)
        self.assertIn('monthly_installment', response.data)

        if response.data['loan_approved']:
            self.loan_id = response.data['loan_id']
        else:
            self.loan_id = None

    def test_view_loan_details(self):
        loan = Loan.objects.create(
            customer=self.customer,
            loan_amount=100000,
            tenure=12,
            interest_rate=12,
            monthly_repayment=10000,
            emis_paid_on_time=0,
            start_date='2024-06-01',
            end_date='2025-06-01'
        )
        url = reverse('view-loan-details', kwargs={'loan_id': loan.id})
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('id', response.data)
        self.assertIn('customer', response.data)

    def test_view_loans_by_customer(self):
        for _ in range(2):                            # CREATING MULTIPLE LOANS FOR THE SAME CUSTOMER
            Loan.objects.create(
                customer=self.customer,
                loan_amount=50000,
                tenure=12,
                interest_rate=12,
                monthly_repayment=5000,
                emis_paid_on_time=0,
                start_date='2025-01-01',
                end_date='2026-01-01'
            )
        url = reverse('view-loans', kwargs={'customer_id': self.customer.id})
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)
        if response.data:
            self.assertIn('id', response.data[0])
            self.assertIn('monthly_repayment', response.data[0])
