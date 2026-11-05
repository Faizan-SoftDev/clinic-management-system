"""Automated tests for the Clinic Management System."""

from copy import deepcopy
from contextlib import redirect_stdout
from io import StringIO
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
    """Run a test and report its result."""
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
    assert result == (False, "Every charge must be a non-negative number.")

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
    assert test_appointments[0]["processed"] is True
    assert test_appointments[0]["status"] == "completed"
    assert test_appointments[0]["bill"]["final_bill"] == 4750
def test_process_appointment_twice():
    test_appointments = [
        {
            "appointment_id": "AT003",
            "patient_id": "P001",
            "doctor_id": "D001",
            "status": "pending",
            "tests": [],
        }
    ]

    first_result = process_appointment(
        "AT003",
        deepcopy(patients),
        deepcopy(doctors),
        test_appointments,
        deepcopy(test_prices),
        deepcopy(CLINIC_CONFIG),
    )

    second_result = process_appointment(
        "AT003",
        deepcopy(patients),
        deepcopy(doctors),
        test_appointments,
        deepcopy(test_prices),
        deepcopy(CLINIC_CONFIG),
    )

    assert first_result[0] is True, f"First processing failed: {first_result}"
    assert second_result[0] is False, (
        f"Duplicate processing was unexpectedly accepted: {second_result}"
    )


def test_clinic_report():
    report = generate_clinic_report(
        patients,
        doctors,
        deepcopy(appointments),
        test_prices,
        CLINIC_CONFIG,
    )

    assert isinstance(report, dict)
    assert len(report) > 0


def test_saved_seed_bills_keep_historical_prices():
    test_doctors = deepcopy(doctors)
    test_doctors["D001"]["fee"] = "invalid"
    report = generate_clinic_report(
        deepcopy(patients),
        test_doctors,
        deepcopy(appointments),
        deepcopy(test_prices),
        deepcopy(CLINIC_CONFIG),
    )

    assert report["total_patient_revenue"] == 13100


def test_doctor_report():
    report = generate_doctor_report(
        patients,
        doctors,
        deepcopy(appointments),
        test_prices,
        CLINIC_CONFIG,
    )

    assert isinstance(report, dict)
    assert len(report) == len(doctors)


def test_patient_report():
    report = generate_patient_report(
        patients,
        doctors,
        deepcopy(appointments),
        test_prices,
        CLINIC_CONFIG,
    )

    assert isinstance(report, dict)
    assert len(report) == len(patients)

def test_cancelled_appointment_cannot_be_processed():
    test_appointments = [{
        "appointment_id": "A100",
        "patient_id": "P001",
        "doctor_id": "D001",
        "status": "cancelled",
        "tests": [],
    }]

    result = process_appointment(
        "A100",
        deepcopy(patients),
        deepcopy(doctors),
        test_appointments,
        deepcopy(test_prices),
        deepcopy(CLINIC_CONFIG),
    )

    assert result[0] is False, (
        f"Cancelled appointment was processed: {result}"
    )


def test_completed_appointment_cannot_be_cancelled():
    test_appointments = [{
        "appointment_id": "A100",
        "patient_id": "P001",
        "doctor_id": "D001",
        "status": "completed",
        "tests": [],
    }]

    result = cancel_appointment("A100", test_appointments)

    assert result[0] is False, (
        f"Completed appointment was cancelled: {result}"
    )

    assert test_appointments[0]["status"] == "completed"


def test_unknown_appointment_cannot_be_processed():
    test_appointments = []

    result = process_appointment(
        "A999",
        deepcopy(patients),
        deepcopy(doctors),
        test_appointments,
        deepcopy(test_prices),
        deepcopy(CLINIC_CONFIG),
    )

    assert result[0] is False, (
        f"Unknown appointment was processed: {result}"
    )


def test_duplicate_appointment_ids_rejected():
    test_appointments = [
        {
            "appointment_id": "A100",
            "patient_id": "P001",
            "doctor_id": "D001",
            "status": "pending",
            "tests": [],
        },
        {
            "appointment_id": "A100",
            "patient_id": "P002",
            "doctor_id": "D003",
            "status": "pending",
            "tests": [],
        },
    ]

    result = process_appointment(
        "A100",
        deepcopy(patients),
        deepcopy(doctors),
        test_appointments,
        deepcopy(test_prices),
        deepcopy(CLINIC_CONFIG),
    )

    assert result[0] is False, (
        f"Duplicate appointment IDs were accepted: {result}"
    )
def test_unavailable_doctor_rejected():
    test_doctors = deepcopy(doctors)

    test_doctors["D001"]["available"] = False

    test_appointments = [{
        "appointment_id": "A100",
        "patient_id": "P001",
        "doctor_id": "D001",
        "status": "pending",
        "tests": [],
    }]

    result = process_appointment(
        "A100",
        deepcopy(patients),
        test_doctors,
        test_appointments,
        deepcopy(test_prices),
        deepcopy(CLINIC_CONFIG),
    )

    assert result[0] is False, (
        f"Unavailable doctor was accepted: {result}"
    )
def test_invalid_patient_age_rejected():
    test_patients = deepcopy(patients)

    test_patients["P001"]["age"] = -5

    result = validate_patient("P001", test_patients)

    assert result[0] is False, (
        f"Patient with negative age was accepted: {result}"
    )
def test_completed_appointment_cannot_be_processed_again():
    test_appointments = [{
        "appointment_id": "A100",
        "patient_id": "P001",
        "doctor_id": "D001",
        "status": "completed",
        "tests": [],
    }]
    result = process_appointment(
        "A100",
        deepcopy(patients),
        deepcopy(doctors),
        test_appointments,
        deepcopy(test_prices),
        deepcopy(CLINIC_CONFIG),
    )

    assert result[0] is False
    assert "completed" in result[1]


def test_test_names_are_case_insensitive():
    result = calculate_bill(
        5000,
        ["ecg"],
        test_prices,
        age=32,
        insurance=False,
    )
    assert result[0] is True
    assert result[1]["test_charges"] == 1500


def test_dashboard_accepts_incomplete_report():
    from reports import print_clinic_dashboard

    output = StringIO()
    with redirect_stdout(output):
        print_clinic_dashboard({})
    assert "Total Senior Citizen Discount: $0.00" in output.getvalue()


if __name__ == "__main__":
    print("\n" + "=" * 45)
    print("CLINIC MANAGEMENT SYSTEM - AUTOMATED TESTS")
    print("=" * 45 + "\n")

    tests = [
        ("Existing patient", test_existing_patient),
        ("Invalid patient", test_invalid_patient),
        ("Existing doctor", test_existing_doctor),
        ("Invalid appointment status", test_invalid_status),
        ("Valid medical tests", test_valid_medical_tests),
        ("Duplicate medical tests", test_duplicate_medical_tests),
        ("Bill without insurance", test_bill_without_insurance),
        ("Bill with insurance", test_bill_with_insurance),
        ("Senior citizen discount", test_senior_citizen_discount),
        ("Invalid consultation fee", test_invalid_consultation_fee),
        ("Invalid total charge", test_calculate_total_rejects_invalid_charges),
        ("Cancel pending appointment", test_cancel_pending_appointment),
        ("Cancel unknown appointment", test_cancel_unknown_appointment),
        ("Process pending appointment", test_process_appointment),
        ("Prevent duplicate processing", test_process_appointment_twice),
        ("Generate clinic report", test_clinic_report),
        ("Seed bills preserve historical prices",
         test_saved_seed_bills_keep_historical_prices),
        ("Generate doctor report", test_doctor_report),
        ("Generate patient report", test_patient_report),
        ("Age 59: no senior discount", test_age_59_no_senior_discount),
        ("Age 60: senior discount", test_age_60_senior_discount),
        ("Negative age rejected", test_negative_age),
        ("Invalid insurance value rejected", test_invalid_insurance_value),
        ("Unknown medical test rejected", test_unknown_medical_test),
        ("Zero fee handled", test_zero_fee),
        ("Cancelled appointment cannot be processed",
         test_cancelled_appointment_cannot_be_processed),

        ("Completed appointment cannot be cancelled",
         test_completed_appointment_cannot_be_cancelled),

        ("Unknown appointment cannot be processed",
         test_unknown_appointment_cannot_be_processed),

        ("Duplicate appointment IDs rejected",
         test_duplicate_appointment_ids_rejected),
        ("Unavailable doctor rejected",
         test_unavailable_doctor_rejected),

        ("Invalid patient age rejected",
         test_invalid_patient_age_rejected),
        ("Completed appointment cannot be processed again",
         test_completed_appointment_cannot_be_processed_again),
        ("Test names are case-insensitive",
         test_test_names_are_case_insensitive),
        ("Dashboard accepts incomplete report",
         test_dashboard_accepts_incomplete_report),
    ]

    for test_name, test_function in tests:
        run_test(test_name, test_function)

    print("\n" + "=" * 45)
    print(f"TOTAL: {passed + failed}")
    print(f"PASSED: {passed}")
    print(f"FAILED: {failed}")
    print("=" * 45)

    if failed:
        print("\nSome tests failed. Check the error messages above.")
    sys.exit(1 if failed else 0)