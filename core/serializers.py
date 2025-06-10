from rest_framework import serializers
from .models import Customer, Loan

class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = '__all__'

class LoanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Loan
        fields = '__all__'


class RegisterCustomerSerializer(serializers.ModelSerializer):
    monthly_income = serializers.FloatField(write_only=True)
    approved_limit = serializers.FloatField(read_only=True)

    class Meta:
        model = Customer
        fields = ['id', 'first_name', 'last_name', 'age', 'phone_number', 'monthly_income', 'approved_limit']

    def create(self, validated_data):
        monthly_income = validated_data.pop('monthly_income')    # EXTRACTING MONTHLY INCOME

        approved_limit = round((36 * monthly_income) / 100000) * 100000     # CALCULATING APPROVED LIMIT(ROUNDED TO NEAREST LAKH)

        validated_data['monthly_salary'] = monthly_income    # MAPPING MONTHLY INCOME TO MODEL FIELD MONTHLY SALARY

        validated_data['approved_limit'] = approved_limit

        return super().create(validated_data)     # CREATING CUSTOMER INSTANCE


class CheckEligibilitySerializer(serializers.Serializer):
    customer_id = serializers.IntegerField()
    loan_amount = serializers.FloatField()
    interest_rate = serializers.FloatField()
    tenure = serializers.IntegerField()



class ViewLoanSerializer(serializers.ModelSerializer):
    customer = serializers.SerializerMethodField()

    class Meta:
        model = Loan
        fields = [
            'id',                                                #LOAN ID
            'customer',
            'loan_amount',
            'interest_rate',
            'monthly_repayment',
            'tenure',
        ]

    def get_customer(self, obj):
        return {
            'id': obj.customer.id,
            'first_name': obj.customer.first_name,
            'last_name': obj.customer.last_name,
            'phone_number': obj.customer.phone_number,
            'age': obj.customer.age,
        }

class LoanSummarySerializer(serializers.ModelSerializer):
    repayments_left = serializers.SerializerMethodField()
    loan_approved = serializers.SerializerMethodField()

    class Meta:
        model = Loan
        fields = ['id', 'loan_amount', 'loan_approved', 'interest_rate', 'monthly_repayment', 'repayments_left']

    def get_repayments_left(self, obj):
        return max(0, obj.tenure - obj.emis_paid_on_time)

    def get_loan_approved(self, obj):
        return True  # ALL LOANS ARE CONSIDERED APPROVED IN THIS CONTEXT
