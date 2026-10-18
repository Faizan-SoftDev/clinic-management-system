# Clinic Management System

## 1. Project Overview

The Clinic Management System is a Python-based application designed
to manage the core operations of a small clinic.

This project was developed as part of a Real-World Problem-Solving
Assessment to demonstrate Python programming fundamentals and
business logic implementation.

The application uses in-memory data structures and does not require
a database, external packages, or a web framework.

## 2. Project Objectives

The main objectives are to:

- Manage patient and doctor information.
- Validate patient and doctor records.
- Manage clinic appointments.
- Process and cancel appointments.
- Calculate consultation and medical test charges.
- Calculate insurance coverage.
- Apply senior citizen discounts.
- Generate clinic, doctor, and patient reports.
- Handle invalid inputs without unnecessarily crashing the program.
- Verify business logic through automated tests.

## 3. Features

### Patient Management
- Display registered patients.
- Validate patient IDs.
- Access patient information.

### Doctor Management
- Display registered doctors.
- Validate doctor IDs.
- Check doctor availability.

### Appointment Management
- Display appointments.
- Add pending appointments.
- Process pending appointments.
- Cancel eligible appointments.
- Prevent duplicate appointment processing.

### Medical Tests
The application supports the medical tests defined in its data:

- ECG
- Blood Test
- X-Ray
- MRI

Medical test prices are configured in `data.py`.

### Billing and Insurance
- Calculate consultation charges.
- Calculate medical test charges.
- Calculate total charges.
- Calculate insurance coverage.
- Apply senior citizen discounts.
- Display the final patient payable amount.### Billing Rules

The system calculates the final patient bill using the following rules:

1. Subtotal = Consultation Fee + Medical Test Charges.
2. Insurance covers 20% of the consultation fee for insured patients.
3. Insurance covers 50% of medical test charges for insured patients.
4. Patients aged 60 or above receive a 10% senior citizen discount on the amount remaining after insurance coverage.
5. The final patient bill is calculated after deducting insurance coverage and any applicable senior citizen discount.
6. Patients without insurance receive no insurance coverage.

Insurance coverage and senior citizen discounts are displayed separately in the clinic dashboard.
## 6. Testing

The project includes a custom automated test suite in `test_clinic.py`.

The tests verify important business rules, including:

- Patient and doctor validation.
- Invalid patient ages.
- Medical test validation.
- Insurance calculations.
- Senior citizen discounts.
- Appointment processing and cancellation.
- Duplicate appointment prevention.
- Doctor availability.
- Invalid appointment IDs.

### Run Tests

Execute the following command from the project directory:

```bash
python3 test_clinic.py
### Reports
The application generates:

- Clinic dashboard.
- Doctor performance reports.
- Patient activity and billing reports.

## 4. Technology and Concepts

- Python 3
- Variables and data types
- Conditional statements
- Loops
- Lists, tuples, sets, and dictionaries
- Functions
- `*args` and `**kwargs`
- Lambda expressions
- List comprehensions
- Input validation
- Exception handling
- Modular programming
- Automated testing

No external Python packages are required.

## 5. Project Structure

```text
clinic-management-system/
├── main.py
├── data.py
├── config.py
├── validation.py
├── billing.py
├── appointments.py
├── reports.py
├── test_clinic.py
└── README.md