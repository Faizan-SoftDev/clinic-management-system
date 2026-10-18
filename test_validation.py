from data import patients, doctors, test_prices
from validation import (
    validate_patient,
    validate_doctor,
    validate_appointment_status,
    validate_tests,
)

print("TEST 1: Existing patient")
print(validate_patient("P001", patients))

print("\nTEST 2: Invalid patient")
print(validate_patient("P999", patients))

print("\nTEST 3: Existing doctor")
print(validate_doctor("D001", doctors))

print("\nTEST 4: Invalid appointment status")
print(validate_appointment_status("unknown"))

print("\nTEST 5: Valid medical tests")
print(validate_tests(["ECG", "MRI"], test_prices))

print("\nTEST 6: Duplicate medical tests")
print(validate_tests(["ECG", "ECG"], test_prices))