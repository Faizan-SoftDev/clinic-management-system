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
- Book appointments with a valid future date and time, preventing a doctor's
  active appointments from sharing a time slot. Times earlier than the current
  local time are rejected when booking for today.
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
Gross Consultation Charges: PKR 12,000.00
Gross Test Charges: PKR 4,000.00
Total Insurance Coverage: PKR 2,250.00
Total Senior Citizen Discount: PKR 650.00
Total Patient Revenue: PKR 13,100.00

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

Start the application from the project directory with either:

```bash
python3 main.py
# or
python3 .
```

Running `data.py` directly only loads the starter records; it does not start
the interactive menu.

Run the dependency-free test suite from the project directory:

```bash
python3 test_clinic.py
```

The tests cover billing and discount calculations, validation, processing and
cancellation, duplicate and unavailable records, case-insensitive tests,
appointment scheduling collisions, malformed report data, reports, and
incomplete dashboard data. `test_clinic.py` also exposes
`test_*` functions that can be collected by pytest if it is available.

## 6. Design decisions

The project follows single-responsibility design without classes, as required
by the assignment: `validation.py` checks input, `billing.py` calculates
charges, `appointments.py` changes appointment state, `reports.py` derives
read-only statistics, and `main.py` only handles terminal input/output.
Functions return `(success, result_or_reason)` so invalid data is rejected
cleanly instead of crashing the program. The configuration is passed into
billing/report functions when needed, while the default remains read-only;
the senior-discount closure demonstrates local and enclosing (LEGB) scope.

## 7. Project structure

```text
clinic-management-system/
├── appointments.py
├── billing.py
├── config.py
├── data.py
├── __main__.py
├── main.py
├── reports.py
├── test_clinic.py
├── validation.py
└── README.md
```
