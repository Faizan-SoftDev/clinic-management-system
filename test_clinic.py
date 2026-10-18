"""Automated tests for the Clinic Management System."""

from copy import deepcopy

from data import patients, doctors, appointments, test_prices
from config import CLINIC_CONFIG

from validation import (
    validate_patient,
    validate_doctor,
    validate_appointment_status,
    validate_tests,
)

from billing import calculate_bill
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
# REVIEW TEST 18: Age 59 should not receive the senior discount.
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


# REVIEW TEST 19: Age 60 should receive the senior discount.
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


# REVIEW TEST 20: Negative age should be rejected.
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


# REVIEW TEST 21: Invalid insurance value should be rejected.
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


# REVIEW TEST 22: Unknown medical test should be rejected.
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


# REVIEW TEST 23: Zero fee should be handled without crashing.
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

# Test 1: Existing patient
def test_existing_patient():
    result = validate_patient("P001", patients)
    assert result[0] is True, f"Unexpected result: {result}"


# Test 2: Non-existing patient
def test_invalid_patient():
    result = validate_patient("P999", patients)
    assert result[0] is False, f"Unexpected result: {result}"


# Test 3: Existing doctor
def test_existing_doctor():
    result = validate_doctor("D001", doctors)
    assert result[0] is True, f"Unexpected result: {result}"


# Test 4: Invalid appointment status
def test_invalid_status():
    result = validate_appointment_status("unknown")
    assert result[0] is False, f"Unexpected result: {result}"


# Test 5: Valid medical tests
def test_valid_medical_tests():
    result = validate_tests(["ECG", "Blood Test"], test_prices)
    assert result[0] is True, f"Unexpected result: {result}"


# Test 6: Duplicate medical tests
def test_duplicate_medical_tests():
    result = validate_tests(["ECG", "ECG"], test_prices)
    assert result[0] is False, f"Unexpected result: {result}"


# Test 7: Bill without insurance
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


# Test 8: Bill with insurance
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


# Test 9: Senior citizen discount
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


# Test 10: Negative consultation fee
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


# Test 11: Cancel a pending appointment
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


# Test 12: Cancel an unknown appointment
def test_cancel_unknown_appointment():
    result = cancel_appointment("UNKNOWN", [])

    assert result[0] is False, f"Unknown appointment was accepted: {result}"


# Test 13: Process a pending appointment
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
        patients,
        doctors,
        test_appointments,
        test_prices,
        CLINIC_CONFIG,
    )

    print("DEBUG result:", result)
    print("DEBUG appointment:", test_appointments[0])

    assert result[0] is True, f"Processing failed: {result}"
    assert test_appointments[0]["processed"] is True
    assert test_appointments[0]["status"] == "completed"
    assert test_appointments[0]["bill"]["final_bill"] == 4750
# Test 14: Prevent processing the same appointment twice
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
        patients,
        doctors,
        test_appointments,
        test_prices,
        CLINIC_CONFIG,
    )

    second_result = process_appointment(
        "AT003",
        patients,
        doctors,
        test_appointments,
        test_prices,
        CLINIC_CONFIG,
    )

    assert first_result[0] is True, f"First processing failed: {first_result}"
    assert second_result[0] is False, (
        f"Duplicate processing was unexpectedly accepted: {second_result}"
    )


# Test 15: Generate clinic report
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


# Test 16: Generate doctor report
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


# Test 17: Generate patient report
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

# REVIEW TEST 24: A cancelled appointment must not be processed.
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
        patients,
        doctors,
        test_appointments,
        test_prices,
        CLINIC_CONFIG,
    )

    assert result[0] is False, (
        f"Cancelled appointment was processed: {result}"
    )


# REVIEW TEST 25: A completed appointment cannot be cancelled.
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


# REVIEW TEST 26: Processing an unknown appointment must fail.
def test_unknown_appointment_cannot_be_processed():
    test_appointments = []

    result = process_appointment(
        "A999",
        patients,
        doctors,
        test_appointments,
        test_prices,
        CLINIC_CONFIG,
    )

    assert result[0] is False, (
        f"Unknown appointment was processed: {result}"
    )


# REVIEW TEST 27: Duplicate appointment IDs must be rejected.
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
        patients,
        doctors,
        test_appointments,
        test_prices,
        CLINIC_CONFIG,
    )

    assert result[0] is False, (
        f"Duplicate appointment IDs were accepted: {result}"
    )
# REVIEW TEST 28: An unavailable doctor cannot receive a new appointment.
def test_unavailable_doctor_rejected():
    test_doctors = {
        doctor_id: doctor.copy()
        for doctor_id, doctor in doctors.items()
    }

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
        patients,
        test_doctors,
        test_appointments,
        test_prices,
        CLINIC_CONFIG,
    )

    assert result[0] is False, (
        f"Unavailable doctor was accepted: {result}"
    )
# REVIEW TEST 29: Invalid patient age must be rejected.
def test_invalid_patient_age_rejected():
    test_patients = {
        patient_id: patient.copy()
        for patient_id, patient in patients.items()
    }

    test_patients["P001"]["age"] = -5

    result = validate_patient("P001", test_patients)

    assert result[0] is False, (
        f"Patient with negative age was accepted: {result}"
    )
# Run all tests
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
        ("Cancel pending appointment", test_cancel_pending_appointment),
        ("Cancel unknown appointment", test_cancel_unknown_appointment),
        ("Process pending appointment", test_process_appointment),
        ("Prevent duplicate processing", test_process_appointment_twice),
        ("Generate clinic report", test_clinic_report),
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