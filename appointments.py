"""Appointment processing and cancellation for the clinic."""

from billing import calculate_bill
from validation import (
    validate_appointment,
    validate_appointment_status,
)


def find_appointment(appointment_id, appointments):
    """Find an appointment by ID without modifying the data."""
    if (
        not isinstance(appointment_id, str)
        or not appointment_id.strip()
        or not isinstance(appointments, list)
    ):
        return None

    for appointment in appointments:
        if (
            isinstance(appointment, dict)
            and appointment.get("appointment_id") == appointment_id
        ):
            return appointment

    return None


def process_appointment(
    appointment_id,
    patients,
    doctors,
    appointments,
    test_prices,
    config=None,
):
    """
    Validate and process an appointment.

    A successful appointment is billed only once.
    Only pending appointments can be processed.
    """
    if not isinstance(appointments, list):
        return False, "Appointments must be provided as a list."

    if not isinstance(appointment_id, str) or not appointment_id.strip():
        return False, "Appointment ID must be a non-empty string."

    appointment = find_appointment(appointment_id, appointments)

    if appointment is None:
        return False, f"Appointment {appointment_id} does not exist."

    if sum(
        1
        for item in appointments
        if isinstance(item, dict)
        and item.get("appointment_id") == appointment_id
    ) > 1:
        return False, f"Duplicate appointment ID {appointment_id} exists."

    if appointment.get("processed") is True:
        return False, f"Appointment {appointment_id} has already been processed."

    status_result = validate_appointment_status(appointment.get("status"))

    if not status_result[0]:
        return False, status_result[1]

    if appointment["status"] != "pending":
        return False, (
            f"Appointment {appointment_id} is {appointment['status']} "
            "and cannot be processed."
        )

    validation_result = validate_appointment(
        appointment,
        patients,
        doctors,
        test_prices,
    )

    if not validation_result[0]:
        return False, validation_result[1]

    patient = patients[appointment["patient_id"]]
    doctor = doctors[appointment["doctor_id"]]

    billing_options = {
        "insurance": patient["insurance"],
        "senior_discount": True,
        "include_tests": True,
    }

    if config is not None:
        billing_options["config"] = config

    bill_result = calculate_bill(
        doctor["fee"],
        appointment["tests"],
        test_prices,
        patient["age"],
        **billing_options,
    )

    if not bill_result[0]:
        return False, bill_result[1]

    # Update the appointment only after validation and billing succeed.
    appointment["bill"] = bill_result[1]
    appointment["processed"] = True
    appointment["status"] = "completed"

    return True, {
        "appointment_id": appointment_id,
        "patient_name": patient["name"],
        "doctor_name": doctor["name"],
        "bill": bill_result[1],
        "message": f"Appointment {appointment_id} processed successfully.",
    }


def cancel_appointment(appointment_id, appointments):
    """
    Cancel a pending appointment.

    Completed and already-cancelled appointments cannot be cancelled.
    """
    if not isinstance(appointments, list):
        return False, "Appointments must be provided as a list."

    if not isinstance(appointment_id, str) or not appointment_id.strip():
        return False, "Appointment ID must be a non-empty string."

    appointment = find_appointment(appointment_id, appointments)

    if appointment is None:
        return False, f"Appointment {appointment_id} does not exist."

    if sum(
        1
        for item in appointments
        if isinstance(item, dict)
        and item.get("appointment_id") == appointment_id
    ) > 1:
        return False, f"Duplicate appointment ID {appointment_id} exists."

    status_result = validate_appointment_status(appointment.get("status"))

    if not status_result[0]:
        return False, status_result[1]

    if appointment["status"] == "completed":
        return False, f"Completed appointment {appointment_id} cannot be cancelled."

    if appointment["status"] == "cancelled":
        return False, f"Appointment {appointment_id} is already cancelled."

    appointment["status"] = "cancelled"

    return True, f"Appointment {appointment_id} cancelled successfully."
