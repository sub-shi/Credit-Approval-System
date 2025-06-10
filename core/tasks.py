# core/tasks.py

from celery import shared_task
import pandas as pd
from core.models import Customer, Loan
from datetime import datetime

CUSTOMER_ID_MAP = {}     # MAPPING EXCEL CUSTOMER ID TO DB CUSTOMER ID

@shared_task
def ingest_customer_data(file_path):
    df = pd.read_excel(file_path)
    print(df.columns)

    global CUSTOMER_ID_MAP
    CUSTOMER_ID_MAP.clear()

    for _, row in df.iterrows():
        customer = Customer.objects.create(
            first_name=row['First Name'],
            last_name=row['Last Name'],
            age=row['Age'],
            phone_number=row['Phone Number'],
            monthly_salary=row['Monthly Salary'],
            approved_limit=row['Approved Limit']
        )
        CUSTOMER_ID_MAP[row['Customer ID']] = customer.id   # SAVING MAPPING OF EXCEL CUSTOMER ID TO DB CUSTOMER ID

    print(f"Customer map: {CUSTOMER_ID_MAP}")

@shared_task
def ingest_loan_data(file_path):
    df = pd.read_excel(file_path)
    print(df.columns)

    global CUSTOMER_ID_MAP
    if not CUSTOMER_ID_MAP:
        all_customers = Customer.objects.all()               # FETCHING ALL CUSTOMERS FROM DB
        CUSTOMER_ID_MAP = {c.id: c.id for c in all_customers}
        print("WARNING: CUSTOMER_ID_MAP was empty, built fallback map")

    for _, row in df.iterrows():
        excel_customer_id = row['Customer ID']
        db_customer_id = CUSTOMER_ID_MAP.get(excel_customer_id)

        if not db_customer_id:
            print(f"Skipping Loan — No matching Customer for Excel ID {excel_customer_id}")
            continue

        customer = Customer.objects.get(id=db_customer_id)

        Loan.objects.create(
            customer=customer,
            loan_amount=row['Loan Amount'],
            tenure=row['Tenure'],
            interest_rate=row['Interest Rate'],
            monthly_repayment=row['Monthly payment'],
            emis_paid_on_time=row.get('EMIs paid on Time', 0),
            start_date=pd.to_datetime(row['Date of Approval']).date(),
            end_date=pd.to_datetime(row['End Date']).date()
        )

    print("Loan ingestion complete!")