# Clinic Management System

A command-line application for managing patients, doctors, appointments, and
billing. Data is stored in Python dictionaries and lists while the application
is running; no third-party packages are required.

## Run the application

From the project directory, run:

```bash
python3 .
```

You can also run `python3 app.py`.

## Run the tests

```bash
python3 test_clinic.py
```

## Billing and reports

Bills include consultation fees and selected medical tests. Insurance covers
20% of consultation fees and 50% of test charges. Patients aged 60 or older
receive a 10% discount after insurance.

Completed appointments keep their bill details so later fee changes do not
change historical totals. The clinic dashboard shows consultation revenue,
test revenue, insurance coverage, senior discounts, and patient revenue. It
also warns when a completed appointment has no bill.

Appointment validation checks patient and doctor details, doctor availability,
medical tests, and duplicate appointment IDs.
