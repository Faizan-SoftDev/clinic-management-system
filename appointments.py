"""Lifecycle management for patient appointments."""

from typing import Dict, List, Any, Tuple
from validation import validate_appointment, validate_appointment_status
from billing import calculate_bill
from config import CLINIC_CONFIG


def book_appointment(
    appointment_id: str,
    patient_id: str,
    doctor_id: str,
    date: str,
    time_slot: str,
    tests: List[str],
    patients: Dict[str, Any],
    doctors: Dict[str, Any],
    test_prices: Dict[str, float],
    appointments: List[Dict[str, Any]],
) -> Tuple[bool, str]:
    """Book a new pending appointment after passing all validation rules."""
    new_app = {
        "appointment_id": appointment_id,
        "patient_id": patient_id,
        "doctor_id": doctor_id,
        "date": date,
        "time_slot": time_slot,
        "tests": tests,
        "status": "pending",
    }

    valid, msg = validate_appointment(new_app, patients, doctors, test_prices, appointments)
    if not valid:
        return False, msg

    appointments.append(new_app)
    return True, f"Appointment '{appointment_id}' successfully booked."


def process_appointment(
    appointment_id: str,
    appointments: List[Dict[str, Any]],
    patients: Dict[str, Any],
    doctors: Dict[str, Any],
    test_prices: Dict[str, float],
    config: Dict[str, Any] = None,
) -> Tuple[bool, str]:
    """Process a pending appointment to completed status and attach its bill."""
    if config is None:
        config = CLINIC_CONFIG

    app = next((a for a in appointments if isinstance(a, dict) and a.get("appointment_id") == appointment_id), None)
    if not app:
        return False, f"Appointment '{appointment_id}' not found."

    if app.get("status") == "completed":
        return False, f"Appointment '{appointment_id}' is already completed."
    if app.get("status") == "cancelled":
        return False, f"Cannot process cancelled appointment '{appointment_id}'."

    patient = patients.get(app["patient_id"], {})
    doctor = doctors.get(app["doctor_id"], {})

    success, res = calculate_bill(
        doctor.get("fee", 0),
        app.get("tests", []),
        test_prices,
        patient.get("age", 0),
        insurance=patient.get("insurance", False),
        senior_discount=True,
        include_tests=True,
        config=config,
    )

    if not success:
        return False, f"Failed to generate bill: {res}"

    app["status"] = "completed"
    app["bill"] = res
    app["processed"] = True
    return True, f"Appointment '{appointment_id}' processed successfully."


def cancel_appointment(appointment_id: str, appointments: List[Dict[str, Any]]) -> Tuple[bool, str]:
    """Cancel an active pending appointment."""
    app = next((a for a in appointments if isinstance(a, dict) and a.get("appointment_id") == appointment_id), None)
    if not app:
        return False, f"Appointment '{appointment_id}' not found."

    if app.get("status") == "completed":
        return False, f"Cannot cancel completed appointment '{appointment_id}'."
    if app.get("status") == "cancelled":
        return False, f"Appointment '{appointment_id}' is already cancelled."

    app["status"] = "cancelled"
    return True, f"Appointment '{appointment_id}' cancelled successfully."