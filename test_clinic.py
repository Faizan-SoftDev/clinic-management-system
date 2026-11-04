"""Automated 28-point test suite for Clinic Management System."""

import subprocess
import sys
from config import CLINIC_CONFIG, create_senior_discount_calculator
from validation import (
    validate_patient,
    validate_doctor,
    validate_appointment_status,
    validate_tests,
    is_non_negative_number,
)
from billing import calculate_bill
from appointments import process_appointment, cancel_appointment, book_appointment
from data import patients, doctors, test_prices, appointments
from reports import generate_clinic_report, print_clinic_dashboard


def run_tests() -> None:
    passed = 0
    total = 0

    def assert_test(condition: bool, description: str):
        nonlocal passed, total
        total += 1
        if condition:
            passed += 1
            print(f"PASS: {description}")
        else:
            print(f"FAIL: {description}")

    print("=================== STARTING CLINIC PORTAL TEST SUITE ===================")

    # 1. Age 59: no senior discount
    calc = create_senior_discount_calculator(CLINIC_CONFIG)
    assert_test(calc(100.0, 59) == 0.0, "Age 59 No Senior Discount")

    # 2. Age 60: senior discount
    assert_test(calc(100.0, 60) == 10.0, "Age 60 Senior Discount Applied")

    # 3. Reject negative age
    ok, _ = calculate_bill(500, [], test_prices, -5)
    assert_test(not ok, "Negative Age Verification Check")

    # 4. Reject invalid insurance value
    ok, _ = calculate_bill(500, [], test_prices, 30, insurance="yes")
    assert_test(not ok, "Invalid Insurance Key Values")

    # 5. Reject unknown medical test
    ok, _ = calculate_bill(500, ["InvalidTest"], test_prices, 30)
    assert_test(not ok, "Unknown Medical Catalog Tests")

    # 6. Allow zero consultation fee
    ok, b = calculate_bill(0, [], test_prices, 30)
    assert_test(ok and b["final_bill"] == 0.0, "Zero Rate Base Fee Setup")

    # 7. Reject invalid charges
    assert_test(not is_non_negative_number(-50), "Rejection of Negative Balances")

    # 8. Find existing patient
    ok, _ = validate_patient("P001", patients)
    assert_test(ok, "Existing Base Patient Index")

    # 9. Reject unknown patient
    ok, _ = validate_patient("P999", patients)
    assert_test(not ok, "Invalid Out-of-bounds Patient ID")

    # 10. Find existing doctor
    ok, _ = validate_doctor("D001", doctors)
    assert_test(ok, "Existing Verified Doctor Profiler")

    # 11. Reject invalid appointment status
    ok, _ = validate_appointment_status("invalid")
    assert_test(not ok, "Unknown Process State Status")

    # 12. Accept valid medical tests
    ok, _ = validate_tests(["ECG", "Blood Test"], test_prices)
    assert_test(ok, "Valid Compound Test Bundles")

    # 13. Reject duplicate medical tests
    ok, _ = validate_tests(["ECG", "ECG"], test_prices)
    assert_test(not ok, "Duplicate Test Request Blocker")

    # 14. Bill without insurance
    ok, b = calculate_bill(5000, ["ECG"], test_prices, 30, insurance=False)
    assert_test(ok and b["final_bill"] == 6500.0, "Standard Billing Without Insurance")

    # 15. Bill with insurance
    ok, b = calculate_bill(5000, ["ECG"], test_prices, 30, insurance=True)
    assert_test(ok and b["final_bill"] == 4750.0, "Standard Billing Coupled With Insurance")

    # 16. Apply senior discount
    ok, b = calculate_bill(5000, ["ECG"], test_prices, 65, insurance=False)
    assert_test(ok and b["final_bill"] == 5850.0, "Senior Citizen Target Discounter")

    # 17. Reject negative consultation fee
    ok, _ = calculate_bill(-100, [], test_prices, 30)
    assert_test(not ok, "Negative Base consultation Rate Block")

    # 18. Cancel pending appointment
    temp_apps = [{"appointment_id": "T001", "patient_id": "P001", "doctor_id": "D001", "status": "pending", "tests": []}]
    ok, _ = cancel_appointment("T001", temp_apps)
    assert_test(ok and temp_apps[0]["status"] == "cancelled", "Cancel Active Pending Logs")

    # 19. Reject cancellation of unknown appointment
    ok, _ = cancel_appointment("T999", temp_apps)
    assert_test(not ok, "Cancel Non-existent Order Records")

    # 20. Process appointment once
    temp_apps = [{"appointment_id": "T002", "patient_id": "P001", "doctor_id": "D001", "status": "pending", "tests": []}]
    ok, _ = process_appointment("T002", temp_apps, patients, doctors, test_prices)
    ok2, _ = process_appointment("T002", temp_apps, patients, doctors, test_prices)
    assert_test(ok and not ok2, "Process System Appointment Lifecycle")

    # 21. Keep historical seed prices
    app_a001 = next(a for a in appointments if a["appointment_id"] == "A001")
    assert_test("bill" in app_a001 and app_a001["bill"]["final_bill"] == 4200.0, "Historical Audit Preservation Integrity")

    # 22. Reject duplicate appointment ID
    ok, _ = book_appointment("A001", "P001", "D001", "2026-11-05", "10:00 AM", [], patients, doctors, test_prices, appointments)
    assert_test(not ok, "Reject Duplicate Appointment ID")

    # 23. Reject unavailable doctor
    temp_docs = {"D999": {"name": "Dr. Off", "specialization": "General", "fee": 1000, "available": False}}
    ok, _ = book_appointment("T003", "P001", "D999", "2026-11-05", "10:00 AM", [], patients, temp_docs, test_prices, appointments)
    assert_test(not ok, "Reject Booking for Unavailable Doctor")

    # 24. Print empty dashboard
    empty_rep = generate_clinic_report({}, {}, [], test_prices)
    assert_test(empty_rep["total_patients"] == 0, "Empty Dashboard Metric Handling")

    # 25. Show dashboard revenue and discounts
    rep = generate_clinic_report(patients, doctors, appointments, test_prices)
    assert_test(rep["patient_revenue"] > 0, "Dashboard Revenue & Senior Discount Totals")

    # 26. Warn when completed appointment has no bill
    temp_apps_nobill = [{"appointment_id": "NB1", "patient_id": "P001", "doctor_id": "D001", "status": "completed"}]
    rep_nobill = generate_clinic_report(patients, doctors, temp_apps_nobill, test_prices)
    assert_test(rep_nobill["completed_without_bill_count"] == 1, "Unbilled Completed Visit Warning Counter")

    # 27. CLI import check
    res = subprocess.run([sys.executable, "-c", "import data, billing, reports; print('DOT_OK')"], capture_output=True, text=True)
    assert_test("DOT_OK" in res.stdout, "System Module Import Execution")

    # 28. Sample bill output validation
    ok, sample_b = calculate_bill(3000, ["Blood Test"], test_prices, 40, insurance=True)
    assert_test(ok and sample_b["final_bill"] == 2900.0, "Sample Billing Formula Calculation")

    print("\n=================== FINAL PERFORMANCE ANALYSIS ===================")
    print(f"Total Tests Executed: {total} | PASSED: {passed} | FAILED: {total - passed}")


if __name__ == "__main__":
    run_tests()