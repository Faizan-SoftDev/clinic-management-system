"""Validation guardrails for clinic data structures and appointments."""

from typing import Dict, List, Any, Tuple


def is_non_negative_number(val: Any) -> bool:
    """Return True if value is an int/float and >= 0."""
    return isinstance(val, (int, float)) and not isinstance(val, bool) and val >= 0


def validate_patient(patient_id: str, patients: Dict[str, Any]) -> Tuple[bool, str]:
    """Validate patient existence."""
    if not isinstance(patient_id, str) or not patient_id.strip():
        return False, "Patient ID must be a non-empty string."
    if not isinstance(patients, dict):
        return False, "Patients repository must be a dictionary."
    if patient_id not in patients:
        return False, f"Patient '{patient_id}' not found."
    return True, "Patient exists."


def validate_patient_data(patient: Dict[str, Any]) -> Tuple[bool, str]:
    """Validate patient demographic schema."""
    if not isinstance(patient, dict):
        return False, "Patient data must be a dictionary."
    if "name" not in patient or not isinstance(patient["name"], str) or not patient["name"].strip():
        return False, "Patient name must be a non-empty string."
    if "age" not in patient or not isinstance(patient["age"], int) or patient["age"] < 0:
        return False, "Patient age must be a non-negative integer."
    return True, "Patient data is valid."


def validate_doctor(doctor_id: str, doctors: Dict[str, Any]) -> Tuple[bool, str]:
    """Validate doctor existence."""
    if not isinstance(doctor_id, str) or not doctor_id.strip():
        return False, "Doctor ID must be a non-empty string."
    if not isinstance(doctors, dict):
        return False, "Doctors repository must be a dictionary."
    if doctor_id not in doctors:
        return False, f"Doctor '{doctor_id}' not found."
    return True, "Doctor exists."


def validate_doctor_availability(doctor_id: str, doctors: Dict[str, Any]) -> Tuple[bool, str]:
    """Validate doctor existence and operational availability."""
    res = validate_doctor(doctor_id, doctors)
    if not res[0]:
        return res
    doc = doctors[doctor_id]
    if not isinstance(doc, dict) or not doc.get("available", True):
        return False, f"Doctor '{doctor_id}' is currently unavailable."
    return True, "Doctor is available."


def validate_doctor_data(doctor: Dict[str, Any]) -> Tuple[bool, str]:
    """Validate doctor profile schema."""
    if not isinstance(doctor, dict):
        return False, "Doctor data must be a dictionary."
    if "name" not in doctor or not isinstance(doctor["name"], str) or not doctor["name"].strip():
        return False, "Doctor name must be a non-empty string."
    if "fee" not in doctor or not is_non_negative_number(doctor["fee"]):
        return False, "Doctor fee must be a non-negative number."
    return True, "Doctor data is valid."


def validate_appointment_status(status: str) -> Tuple[bool, str]:
    """Check status against valid choices."""
    allowed = {"pending", "completed", "cancelled"}
    if not isinstance(status, str) or status not in allowed:
        return False, f"Invalid appointment status '{status}'. Must be one of: {allowed}"
    return True, "Valid appointment status."


def validate_tests(tests: List[str], test_prices: Dict[str, float]) -> Tuple[bool, str]:
    """Validate medical test lists and reject unknown or duplicate tests."""
    if not isinstance(tests, list):
        return False, "Tests must be provided as a list."
    if not isinstance(test_prices, dict):
        return False, "Test prices must be provided as a dictionary."

    normalized_prices = {}
    for name, price in test_prices.items():
        if not isinstance(name, str):
            return False, "All test directory master keys must be strings."
        if not is_non_negative_number(price):
            return False, f"Invalid price setup for medical test '{name}'."
        normalized_prices[name.casefold()] = price

    seen_tests = set()
    for test in tests:
        if not isinstance(test, str) or not test.strip():
            return False, "Test name must be a non-empty string."
        norm_test = test.casefold()
        if norm_test not in normalized_prices:
            return False, f"Unknown medical test '{test}'."
        if norm_test in seen_tests:
            return False, f"Duplicate medical test '{test}' is not allowed."
        seen_tests.add(norm_test)

    return True, "All medical tests are valid."


def validate_appointment(
    appointment: Dict[str, Any],
    patients: Dict[str, Any],
    doctors: Dict[str, Any],
    test_prices: Dict[str, float],
    active_appointments: Any = None,
) -> Tuple[bool, str]:
    """Validate appointment structure, dependencies, and duplicate ID presence."""
    if not isinstance(appointment, dict):
        return False, "Appointment must be a dictionary."

    app_id = appointment.get("appointment_id")
    if not isinstance(app_id, str) or not app_id.strip():
        return False, "Appointment ID must be a non-empty string."

    pid = appointment.get("patient_id")
    res = validate_patient(pid, patients)
    if not res[0]:
        return res
    res = validate_patient_data(patients[pid])
    if not res[0]:
        return False, f"Invalid data for patient {pid}: {res[1]}"

    did = appointment.get("doctor_id")
    res = validate_doctor_availability(did, doctors)
    if not res[0]:
        return res
    res = validate_doctor_data(doctors[did])
    if not res[0]:
        return False, f"Invalid data for doctor {did}: {res[1]}"

    res = validate_appointment_status(appointment.get("status", "pending"))
    if not res[0]:
        return res

    res = validate_tests(appointment.get("tests", []), test_prices)
    if not res[0]:
        return res

    if active_appointments:
        apps_list = active_appointments.values() if isinstance(active_appointments, dict) else active_appointments
        for active in apps_list:
            if isinstance(active, dict) and active.get("appointment_id") == app_id:
                return False, f"Appointment ID '{app_id}' already exists."

    return True, "Appointment data is valid."