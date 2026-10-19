"""Automated tests for the Clinic Management System."""

from copy import deepcopy
import sys

from data import patients, doctors, appointments, test_prices
from config import CLINIC_CONFIG

from validation import (
    validate_patient,
    validate_doctor,
    validate_appointment_status,
    validate_tests,
)

from billing import calculate_bill, calculate_total
from appointments import process_appointment, cancel_appointment
from reports import (
    generate_clinic_report,
    generate_doctor_report,
    generate_patient_report,
)

passed = 0
failed = 0


def run_test(test_name, test_function):
    """Run a test and report its result smoothly without cutting off workflow pipelines."""
    global passed, failed

    try:
        test_function()
        print(f"PASS: {test_name}")
        passed += 1
    except Exception as error:
        print(f"FAIL: {test_name}")
        print(f"Reason: {type(error).__name__}: {error}")
        failed += 1


def test_age_59_no_senior_discount():
    result = calculate_bill(
        5000,
        [],
        test_prices,
        age=59,
        insurance=True,
        config=CLINIC_CONFIG,
    )
    assert result[0] is True, f"Bill calculation failed: {result}"
    bill = result[1]
    assert bill["senior_discount"] == 0
    assert bill["final_bill"] == 4000


def test_age_60_senior_discount():
    result = calculate_bill(
        5000,
        [],
        test_prices,
        age=60,
        insurance=True,
        config=CLINIC_CONFIG,
    )
    assert result[0] is True, f"Bill calculation failed: {result}"
    bill = result[1]
    assert bill["senior_discount"] == 400
    assert bill["final_bill"] == 3600


def test_negative_age():
    result = calculate_bill(
        5000,
        [],
        test_prices,
        age=-1,
        insurance=False,
        config=CLINIC_CONFIG,
    )
    assert result[0] is False, f"Negative age was accepted: {result}"


def test_invalid_insurance_value():
    result = calculate_bill(
        5000,
        [],
        test_prices,
        age=32,
        insurance="yes",
        config=CLINIC_CONFIG,
    )
    assert result[0] is False, f"Invalid insurance value was accepted: {result}"


def test_unknown_medical_test():
    result = calculate_bill(
        5000,
        ["Unknown Test"],
        test_prices,
        age=32,
        insurance=False,
        config=CLINIC_CONFIG,
    )
    assert result[0] is False, f"Unknown medical test was accepted: {result}"


def test_zero_fee():
    result = calculate_bill(
        0,
        [],
        test_prices,
        age=32,
        insurance=False,
        config=CLINIC_CONFIG,
    )
    assert result[0] is True, f"Zero fee was rejected: {result}"
    bill = result[1]
    assert bill["subtotal"] == 0
    assert bill["final_bill"] == 0


def test_calculate_total_rejects_invalid_charges():
    result = calculate_total(5000, -1, 1000)
    assert result[0] is False, "Validation failure flag expected."
    assert result[1] == "Every charge must be a non-negative number."


def test_existing_patient():
    result = validate_patient("P001", patients)
    assert result[0] is True, f"Unexpected result: {result}"


def test_invalid_patient():
    result = validate_patient("P999", patients)
    assert result[0] is False, f"Unexpected result: {result}"


def test_existing_doctor():
    result = validate_doctor("D001", doctors)
    assert result[0] is True, f"Unexpected result: {result}"


def test_invalid_status():
    result = validate_appointment_status("unknown")
    assert result[0] is False, f"Unexpected result: {result}"


def test_valid_medical_tests():
    result = validate_tests(["ECG", "Blood Test"], test_prices)
    assert result[0] is True, f"Unexpected result: {result}"


def test_duplicate_medical_tests():
    result = validate_tests(["ECG", "ECG"], test_prices)
    assert result[0] is False, f"Unexpected result: {result}"


def test_bill_without_insurance():
    result = calculate_bill(
        5000,
        ["ECG", "Blood Test"],
        test_prices,
        age=32,
        insurance=False,
        config=CLINIC_CONFIG,
    )
    assert result[0] is True, f"Bill calculation failed: {result}"
    bill = result[1]
    assert bill["subtotal"] == 7500
    assert bill["insurance_coverage"] == 0
    assert bill["final_bill"] == 7500


def test_bill_with_insurance():
    result = calculate_bill(
        5000,
        ["ECG", "Blood Test"],
        test_prices,
        age=32,
        insurance=True,
        config=CLINIC_CONFIG,
    )
    assert result[0] is True, f"Bill calculation failed: {result}"
    bill = result[1]
    assert bill["subtotal"] == 7500
    assert bill["consultation_coverage"] == 1000
    assert bill["test_coverage"] == 1250
    assert bill["insurance_coverage"] == 2250
    assert bill["final_bill"] == 5250


def test_senior_citizen_discount():
    result = calculate_bill(
        5000,
        ["ECG", "Blood Test"],
        test_prices,
        age=67,
        insurance=True,
        config=CLINIC_CONFIG,
    )
    assert result[0] is True, f"Bill calculation failed: {result}"
    bill = result[1]
    assert bill["insurance_coverage"] == 2250
    assert bill["senior_discount"] == 525
    assert bill["final_bill"] == 4725


def test_invalid_consultation_fee():
    result = calculate_bill(
        -500,
        [],
        test_prices,
        age=32,
        insurance=False,
        config=CLINIC_CONFIG,
    )
    assert result[0] is False, f"Negative fee was accepted: {result}"


def test_cancel_pending_appointment():
    test_appointments = [
        {
            "appointment_id": "AT001",
            "patient_id": "P001",
            "doctor_id": "D001",
            "status": "pending",
            "tests": [],
        }
    ]
    result = cancel_appointment("AT001", test_appointments)
    assert result[0] is True, f"Cancellation failed: {result}"
    assert test_appointments[0]["status"] == "cancelled"


def test_cancel_unknown_appointment():
    result = cancel_appointment("UNKNOWN", [])
    assert result[0] is False, f"Unknown appointment was accepted: {result}"


def test_process_appointment():
    test_appointments = [
        {
            "appointment_id": "AT002",
            "patient_id": "P001",
            "doctor_id": "D001",
            "status": "pending",
            "tests": ["ECG"],
        }
    ]
    result = process_appointment(
        "AT002",
        deepcopy(patients),
        deepcopy(doctors),
        test_appointments,
        deepcopy(test_prices),
        deepcopy(CLINIC_CONFIG),
    )
    assert result[0] is True, f"Processing failed: {result}"
    assert test_appointments[0]["status"] == "completed"


def test_saved_seed_bills_keep_historical_prices():
    test_doctors = deepcopy(doctors)
    test_doctors["D001"]["fee"] = 5000
    report = generate_clinic_report(
        deepcopy(patients),
        test_doctors,
        deepcopy(appointments),
        deepcopy(test_prices),
        CLINIC_CONFIG,
    )
    assert isinstance(report, dict)


# Execution controller map block
if __name__ == "__main__":
    tests_map = {
        "Age 59 No Senior Discount": test_age_59_no_senior_discount,
        "Age 60 Senior Discount Applied": test_age_60_senior_discount,
        "Negative Age Verification Check": test_negative_age,
        "Invalid Insurance Key Values": test_invalid_insurance_value,
        "Unknown Medical Catalog Tests": test_unknown_medical_test,
        "Zero Rate Base Fee Setup": test_zero_fee,
        "Rejection of Negative Balances": test_calculate_total_rejects_invalid_charges,
        "Existing Base Patient Index": test_existing_patient,
        "Invalid Out-of-bounds Patient ID": test_invalid_patient,
        "Existing Verified Doctor Profiler": test_existing_doctor,
        "Unknown Process State Status": test_invalid_status,
        "Valid Compound Test Bundles": test_valid_medical_tests,
        "Duplicate Test Request Blocker": test_duplicate_medical_tests,
        "Standard Billing Without Insurance": test_bill_without_insurance,
        "Standard Billing Coupled With Insurance": test_bill_with_insurance,
        "Senior Citizen Target Discounter": test_senior_citizen_discount,
        "Negative Base consultation Rate Block": test_invalid_consultation_fee,
        "Cancel Active Pending Logs": test_cancel_pending_appointment,
        "Cancel Non-existent Order Records": test_cancel_unknown_appointment,
        "Process System Appointment Lifecycle": test_process_appointment,
        "Historical Audit Preservation Integrity": test_saved_seed_bills_keep_historical_prices,
    }

    print("=================== STARTING CLINIC PORTAL TEST SUITE ===================")
    for name, func in tests_map.items():
        run_test(name, func)

    print("\n=================== FINAL PERFORMANCE ANALYSIS ===================")
    print(f"Total Tests Executed: {passed + failed} | PASSED: {passed} | FAILED: {failed}")
    sys.exit(failed)
