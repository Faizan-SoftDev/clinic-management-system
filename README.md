# Clinic Management System

## 1. Overview

A small command-line clinic application demonstrating Python fundamentals
through patient and doctor records, appointment processing, billing, and
management reports. All records live in Python dictionaries and lists;
there is no database, file storage, framework, or third-party dependency.

## 2. Features and billing rules

- Manage patients, doctors, appointments, and medical tests.
- Validate appointment details and reject invalid or duplicate operations
  with a reason.
- Process pending appointments once and cancel pending appointments.
- Generate clinic, doctor, and patient reports.
- Support configurable billing options through `**kwargs`, and total multiple
  charges with `*args`.

The subtotal is the consultation fee plus requested test charges. Insurance
covers 20% of consultation and 50% of tests. Patients aged 60 or older receive
a 10% discount on the remaining amount after insurance. The discount and
coverage rates are held in `config.py`. Seed completed appointments store
their bills at initialization, so later price changes do not reprice history.

Test names are accepted case-insensitively, and repeated tests are rejected.
When report values tie, the first item in the source insertion order is
selected.

## 3. Design notes

- Business operations return `(success, result_or_reason)` rather than
  displaying output; the command-line interface handles presentation.
- `calculate_total(*charges)` returns the sum, or `(False, reason)` for invalid
  charges. `calculate_bill(..., **options)` supports `insurance`,
  `senior_discount`, `include_tests`, and `config`.
- The senior-discount calculator is a closure: it captures the age threshold
  and discount rate from its enclosing configuration scope. The billing
  function uses its local `config` binding, falling back to the imported
  module-level `CLINIC_CONFIG`; it does not mutate global configuration. This
  illustrates LEGB lookup (Local, Enclosing, Global, Built-in).
- Reports return dictionaries, while `print_clinic_dashboard` and the CLI
  format and print those results.

## 4. Sample dashboard

```text
================================================
              CLINIC DASHBOARD
================================================
Total Patients: 4
Total Doctors: 3
Total Appointments: 4
Completed: 3
Cancelled: 1
Pending: 0
Total Consultation Revenue: $12,000.00
Total Test Revenue: $4,000.00
Total Insurance Coverage: $3,250.00
Total Senior Citizen Discount: $650.00
Total Patient Revenue: $13,100.00
Most Requested Specialization: Cardiology
Highest Spending Patient: Usman Ali
Most Requested Doctor: Dr. Hassan
Patient with Most Appointments: Ali Khan
Patients without Completed Appointments: P003
Insured Patients: P001, P003
Senior Citizen Patients: P004
================================================
```

## 5. Tests

Run the dependency-free test suite from the project directory:

```bash
python3 test_clinic.py
```

The tests cover billing and discount calculations, validation, processing and
cancellation, duplicate and unavailable records, case-insensitive tests,
reports, and incomplete dashboard data. `test_clinic.py` also exposes
`test_*` functions that can be collected by pytest if it is available.

## 6. Project structure

```text
clinic-management-system/
├── appointments.py
├── billing.py
├── config.py
├── data.py
├── main.py
├── reports.py
├── test_clinic.py
├── validation.py
└── README.md
```