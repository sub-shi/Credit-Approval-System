# Credit Approval System

This is a Django-based Credit Approval System with REST APIs for customer registration, loan eligibility checking, and loan management. It uses Celery for background tasks and Redis as a message broker. The project includes Docker support for easy setup and deployment.

---

## Features

- Customer registration with automatic approved limit calculation
- Loan eligibility check with credit score logic and custom business rules
- Loan creation and management
- Admin interface for managing customers and loans
- Background data ingestion using Celery
- Dockerized setup for development and production

---

## Requirements

- Python 3.11+
- Docker & Docker Compose (recommended)
- Redis (for Celery)
- PostgreSQL or SQLite(Optional)

---

## Quick Start (with Docker)

1. **Clone the repository:**
    ```sh
    git clone <your-repo-url>
    cd Credit Approval System
    ```

2. **Copy and configure environment variables:**
    - Create a `.env` file if needed for your Django/DB settings.

3. **Build and start the services:**
    ```sh
    docker-compose up --build
    ```

4. **Apply migrations and create a superuser:**
    ```sh
    docker-compose exec web python manage.py migrate
    docker-compose exec web python manage.py createsuperuser
    ```

5. **Access the app:**
    - API: [http://localhost:8000/](http://localhost:8000/)
    - Admin: [http://localhost:8000/admin/](http://localhost:8000/admin/)

---

## Running Locally (without Docker)

1. **Create and activate a virtual environment:**
    ```sh
    python -m venv .venv
    source .venv/bin/activate  # On Windows: .venv\Scripts\activate
    ```

2. **Install dependencies:**
    ```sh
    pip install -r requirements.txt
    ```

3. **Apply migrations and create a superuser:**
    ```sh
    python manage.py migrate
    python manage.py createsuperuser
    ```

4. **Start Redis (required for Celery):**
    - Make sure Redis is running on `localhost:6379`.

5. **Run the development server:**
    ```sh
    python manage.py runserver
    ```

6. **Start Celery worker:**
    ```sh
    celery -A credit_approval_system worker -l info
    ```

---

## Data Ingestion

- Use the provided Celery tasks to ingest customer and loan data from Excel files.
- Example (from Django shell):
    ```python
    from core.tasks import ingest_customer_data, ingest_loan_data
    ingest_customer_data.delay('path/to/customer_file.xlsx')
    ingest_loan_data.delay('path/to/loan_file.xlsx')
    ```

---

## Useful Scripts

- `wait-for-it.sh`: Used in Docker to wait for services like the database or Redis to be ready before starting Django or Celery.

---

## API Endpoints

- `POST /register/` — Register a new customer
- `POST /check-eligibility/` — Check loan eligibility
- `POST /create-loan/` — Create a new loan
- `GET /view-loan/<loan_id>/` — View loan details
- `GET /view-loans/<customer_id>/` — View all loans for a customer

---

## Running Tests

To run the automated API tests, use:

```sh
python manage.py test core
```

This will run all tests in `core/tests.py` and verify that your API endpoints are working as expected.

---

## License

This project is for educational/demo purposes.

---

## Notes for Protection

- Replace DEBUG=True with DEBUG=False and configure allowed hosts.

- Use a production-ready DB like PostgreSQL.

- Set up proper environment variables and secrets management.

--- 

**Happy Coding!**