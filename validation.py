"""Validation functions for the Clinic Management System."""

VALID_STATUSES = {"pending", "completed", "cancelled"}


def is_non_negative_number(value):
    """Return whether value is a non-negative int or float, excluding bools."""
    return (
        not isinstance(value, bool)
        and isinstance(value, (int, float))
        and value >= 0
    )


def validate_patient(patient_id, patients):
    if not isinstance(patient_id, str) or not patient_id.strip():
        return False, "Patient ID must be a non-empty string."

    if not isinstance(patients, dict):
        return False, "Patients must be provided as a dictionary."

    if patient_id not in patients:
        return False, f"Patient {patient_id} does not exist."

    patient = patients[patient_id]

    if not isinstance(patient, dict):
        return False, "Patient data must be a dictionary."

    age = patient.get("age")

    if isinstance(age, bool) or not isinstance(age, int) or age < 0:
        return False, "Patient age must be a non-negative integer."

    return True, "Patient exists."


def validate_doctor(doctor_id, doctors):
    """Check whether a doctor exists."""
    if not isinstance(doctor_id, str) or not doctor_id.strip():
        return False, "Doctor ID must be a non-empty string."

    if not isinstance(doctors, dict):
        return False, "Doctors must be provided as a dictionary."

    if doctor_id not in doctors:
        return False, f"Doctor {doctor_id} does not exist."

    return True, "Doctor exists."


def validate_doctor_availability(doctor_id, doctors):
    """Check whether an existing doctor is available."""
    result = validate_doctor(doctor_id, doctors)

    if not result[0]:
        return result

    if doctors[doctor_id].get("available") is not True:
        return False, f"Doctor {doctor_id} is not available."

    return True, "Doctor is available."


def validate_appointment_status(status):
    """Accept only the supported appointment statuses."""
    if not isinstance(status, str):
        return False, "Appointment status must be a string."

    if status not in VALID_STATUSES:
        return False, (
            f"Invalid appointment status '{status}'. "
            f"Allowed statuses: {', '.join(sorted(VALID_STATUSES))}."
        )

    return True, "Appointment status is valid."


def validate_tests(tests, test_prices):
    """Check that test names and prices are valid."""
    if not isinstance(tests, list):
        return False, "Tests must be provided as a list."

    if not isinstance(test_prices, dict):
        return False, "Test prices must be provided as a dictionary."

    for name, price in test_prices.items():
        if not isinstance(name, str):
            return False, "All test names must be strings."
        if not is_non_negative_number(price):
            return False, f"Invalid price for test '{name}'."

    normalized_prices = {name.casefold(): price for name, price in test_prices.items()}
    seen_tests = set()

    for test in tests:
        if not isinstance(test, str) or not test.strip():
            return False, "Each test name must be a non-empty string."

        normalized_test = test.casefold()

        if normalized_test not in normalized_prices:
            return False, f"Medical test '{test}' does not exist."

        if normalized_test in seen_tests:
            return False, f"Duplicate medical test '{test}' is not allowed."

        seen_tests.add(normalized_test)

    return True, "All medical tests are valid."


def validate_patient_data(patient):
    """Validate the required patient fields and age."""
    if not isinstance(patient, dict):
        return False, "Patient data must be a dictionary."

    name = patient.get("name")
    age = patient.get("age")
    city = patient.get("city")
    insurance = patient.get("insurance")

    if not isinstance(name, str) or not name.strip():
        return False, "Patient name must be a non-empty string."

    if isinstance(age, bool) or not isinstance(age, int) or age < 0:
        return False, "Patient age must be a non-negative integer."

    if not isinstance(city, str) or not city.strip():
        return False, "Patient city must be a non-empty string."

    if not isinstance(insurance, bool):
        return False, "Patient insurance must be True or False."

    return True, "Patient data is valid."


def validate_doctor_data(doctor):
    """Validate the required doctor fields."""
    if not isinstance(doctor, dict):
        return False, "Doctor data must be a dictionary."

    name = doctor.get("name")
    specialization = doctor.get("specialization")
    fee = doctor.get("fee")
    available = doctor.get("available")

    if not isinstance(name, str) or not name.strip():
        return False, "Doctor name must be a non-empty string."

    if not isinstance(specialization, str) or not specialization.strip():
        return False, "Doctor specialization must be a non-empty string."

    if not is_non_negative_number(fee):
        return False, "Doctor fee must be a non-negative number."

    if not isinstance(available, bool):
        return False, "Doctor availability must be True or False."

    return True, "Doctor data is valid."


def validate_appointment(
    appointment,
    patients,
    doctors,
    test_prices,
    appointments=None,
):
    """Validate an appointment fully."""
    if not isinstance(appointment, dict):
        return False, "Appointment must be a dictionary."

    appointment_id = appointment.get("appointment_id")
    if not isinstance(appointment_id, str) or not appointment_id.strip():
        return False, "Appointment ID must be a non-empty string."

    if appointments is not None:
        if not isinstance(appointments, list):
            return False, "Appointments must be provided as a list."
        if any(
            isinstance(existing, dict)
            and existing is not appointment
            and existing.get("appointment_id") == appointment_id
            for existing in appointments
        ):
            return False, f"Appointment ID {appointment_id} already exists."

    patient_id = appointment.get("patient_id")
    result = validate_patient(patient_id, patients)
    if not result[0]:
        return result

    doctor_id = appointment.get("doctor_id")
    result = validate_doctor_availability(doctor_id, doctors)
    if not result[0]:
        return result

    result = validate_doctor_data(doctors[doctor_id])
    if not result[0]:
        return False, f"Invalid data for doctor {doctor_id}: {result[1]}"

    result = validate_appointment_status(appointment.get("status"))
    if not result[0]:
        return result

    result = validate_tests(appointment.get("tests"), test_prices)
    if not result[0]:
        return result

    return True, "Appointment data is valid."