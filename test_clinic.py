"""Automated tests for the Clinic Management System."""

from copy import deepcopy
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
import subprocess
import sys
from unittest.mock import patch

from data import patients, doctors, appointments, test_prices
from config import CLINIC_CONFIG

from validation import (
    validate_patient,
    validate_doctor,
    validate_appointment_status,
    validate_appointment,
    validate_tests,
)

from billing import calculate_bill, calculate_total
from appointments import process_appointment, cancel_appointment
from reports import (
    generate_clinic_report,
    generate_doctor_report,
    generate_patient_report,
    print_clinic_dashboard,
)
from main import handle_sample_bill

passed = 0
failed = 0


def run_test(test_name, test_function):
    """Run one test and report its result."""
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
    repeated_result = process_appointment(
        "AT002",
        deepcopy(patients),
        deepcopy(doctors),
        test_appointments,
        deepcopy(test_prices),
        deepcopy(CLINIC_CONFIG),
    )
    assert repeated_result[0] is False, "An appointment was processed twice."


def test_saved_seed_bills_keep_historical_prices():
    test_doctors = deepcopy(doctors)
    test_doctors["D001"]["fee"] = 99999
    report = generate_clinic_report(
        deepcopy(patients),
        test_doctors,
        deepcopy(appointments),
        deepcopy(test_prices),
        CLINIC_CONFIG,
    )
    assert report["patient_revenue"] == 13100


def test_duplicate_appointment_id_is_rejected_by_validation():
    new_appointment = {
        "appointment_id": "A001",
        "patient_id": "P001",
        "doctor_id": "D001",
        "status": "pending",
        "tests": [],
    }
    result = validate_appointment(
        new_appointment,
        deepcopy(patients),
        deepcopy(doctors),
        deepcopy(test_prices),
        deepcopy(appointments),
    )
    assert result[0] is False
    assert "already exists" in result[1]


def test_unavailable_doctor_is_rejected():
    test_doctors = deepcopy(doctors)
    test_doctors["D001"]["available"] = False
    new_appointment = {
        "appointment_id": "AT003",
        "patient_id": "P001",
        "doctor_id": "D001",
        "status": "pending",
        "tests": [],
    }
    result = validate_appointment(
        new_appointment,
        deepcopy(patients),
        test_doctors,
        deepcopy(test_prices),
        [],
    )
    assert result[0] is False
    assert "not available" in result[1]


def test_empty_dashboard_report_prints_defaults():
    output = StringIO()
    with redirect_stdout(output):
        print_clinic_dashboard({})
    dashboard = output.getvalue()
    assert "Total Patients: 0" in dashboard
    assert "Total Patient Revenue: $0.00" in dashboard


def test_dashboard_revenue_and_senior_discount_totals():
    report = generate_clinic_report(
        deepcopy(patients),
        deepcopy(doctors),
        deepcopy(appointments),
        deepcopy(test_prices),
        CLINIC_CONFIG,
    )
    assert report["consultation_revenue"] == 11000
    assert report["test_revenue"] == 2750
    assert report["senior_discounts"] == 650
    assert report["patient_revenue"] == 13100

    output = StringIO()
    with redirect_stdout(output):
        print_clinic_dashboard(report)
    assert "Total Senior Discounts: $650.00" in output.getvalue()


def test_completed_appointment_without_bill_is_reported():
    test_appointments = deepcopy(appointments)
    test_appointments.append(
        {
            "appointment_id": "AT004",
            "patient_id": "P001",
            "doctor_id": "D001",
            "status": "completed",
            "tests": [],
        }
    )
    report = generate_clinic_report(
        deepcopy(patients),
        deepcopy(doctors),
        test_appointments,
        deepcopy(test_prices),
        CLINIC_CONFIG,
    )
    assert report["completed"] == 4
    assert report["patient_revenue"] == 13100
    assert report["completed_without_bill_count"] == 1

    output = StringIO()
    with redirect_stdout(output):
        print_clinic_dashboard(report)
    assert "Warning: 1 completed appointment has no bill." in output.getvalue()


def test_python3_dot_starts_the_application():
    project_dir = Path(__file__).resolve().parent
    result = subprocess.run(
        [sys.executable, "."],
        cwd=project_dir,
        input="0\n",
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    assert "CLINIC MANAGEMENT PORTAL" in result.stdout


def test_sample_bill_accepts_tests_and_prints_bill_lines():
    output = StringIO()
    with patch("builtins.input", side_effect=["P001", "D001", "ECG, Blood Test"]):
        with redirect_stdout(output):
            handle_sample_bill()
    bill_output = output.getvalue()
    assert "Test charges: $2,500.00" in bill_output
    assert "Final bill: $5,250.00" in bill_output
    assert "Simulated Matrix Output" not in bill_output


if __name__ == "__main__":
    tests_map = {
        "Age 59: no senior discount": test_age_59_no_senior_discount,
        "Age 60: senior discount": test_age_60_senior_discount,
        "Reject negative age": test_negative_age,
        "Reject invalid insurance value": test_invalid_insurance_value,
        "Reject unknown medical test": test_unknown_medical_test,
        "Allow zero consultation fee": test_zero_fee,
        "Reject invalid charges": test_calculate_total_rejects_invalid_charges,
        "Find existing patient": test_existing_patient,
        "Reject unknown patient": test_invalid_patient,
        "Find existing doctor": test_existing_doctor,
        "Reject invalid appointment status": test_invalid_status,
        "Accept valid medical tests": test_valid_medical_tests,
        "Reject duplicate medical tests": test_duplicate_medical_tests,
        "Bill without insurance": test_bill_without_insurance,
        "Bill with insurance": test_bill_with_insurance,
        "Apply senior discount": test_senior_citizen_discount,
        "Reject negative consultation fee": test_invalid_consultation_fee,
        "Cancel pending appointment": test_cancel_pending_appointment,
        "Reject cancellation of unknown appointment": test_cancel_unknown_appointment,
        "Process appointment once": test_process_appointment,
        "Keep historical seed prices": test_saved_seed_bills_keep_historical_prices,
        "Reject duplicate appointment ID": test_duplicate_appointment_id_is_rejected_by_validation,
        "Reject unavailable doctor": test_unavailable_doctor_is_rejected,
        "Print empty dashboard": test_empty_dashboard_report_prints_defaults,
        "Show dashboard revenue and discounts": test_dashboard_revenue_and_senior_discount_totals,
        "Warn when completed appointment has no bill": test_completed_appointment_without_bill_is_reported,
        "Run application with python3 dot": test_python3_dot_starts_the_application,
        "Print sample bill with selected tests": test_sample_bill_accepts_tests_and_prints_bill_lines,
    }

    print("=================== CLINIC MANAGEMENT TESTS ===================")
    for name, func in tests_map.items():
        run_test(name, func)

    print("\n=================== TEST SUMMARY ===================")
    print(f"Total Tests Executed: {passed + failed} | PASSED: {passed} | FAILED: {failed}")
    sys.exit(failed)
