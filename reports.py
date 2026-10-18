"""Management reports for the Clinic Management System."""

from billing import calculate_bill


def _get_bill(appointment, patients, doctors, test_prices, config=None):
    """Calculate or retrieve a valid bill for a completed appointment."""
    if not isinstance(appointment, dict):
        return None

    if appointment.get("status") != "completed":
        return None

    patient_id = appointment.get("patient_id")
    doctor_id = appointment.get("doctor_id")

    if patient_id not in patients or doctor_id not in doctors:
        return None

    patient = patients[patient_id]
    doctor = doctors[doctor_id]

    if not isinstance(patient, dict) or not isinstance(doctor, dict):
        return None

    options = {
        "insurance": patient.get("insurance"),
        "senior_discount": True,
        "include_tests": True,
    }

    if config is not None:
        options["config"] = config

    result = calculate_bill(
        doctor.get("fee"),
        appointment.get("tests"),
        test_prices,
        patient.get("age"),
        **options,
    )

    if not result[0]:
        return None

    # Use the saved bill for an appointment already processed.
    saved_bill = appointment.get("bill")

    if appointment.get("processed") is True and isinstance(saved_bill, dict):
        return saved_bill

    return result[1]


def _valid_appointments(appointments):
    """Return appointment records with valid, non-empty IDs."""
    if not isinstance(appointments, list):
        return []

    return [
        appointment
        for appointment in appointments
        if isinstance(appointment, dict)
        and isinstance(appointment.get("appointment_id"), str)
        and appointment["appointment_id"].strip()
    ]


def generate_doctor_report(
    patients, doctors, appointments, test_prices, config=None
):
    """Generate statistics for every doctor."""
    if not isinstance(patients, dict) or not isinstance(doctors, dict):
        return {}

    records = _valid_appointments(appointments)
    report = {}

    for doctor_id, doctor in doctors.items():
        if not isinstance(doctor, dict):
            continue

        doctor_appointments = [
            item for item in records
            if item.get("doctor_id") == doctor_id
        ]

        completed = [
            item for item in doctor_appointments
            if item.get("status") == "completed"
        ]

        cancelled = [
            item for item in doctor_appointments
            if item.get("status") == "cancelled"
        ]

        bills = [
            _get_bill(item, patients, doctors, test_prices, config)
            for item in completed
        ]

        bills = [bill for bill in bills if bill is not None]

        revenue = sum(bill["final_bill"] for bill in bills)
        average_bill = revenue / len(bills) if bills else 0

        report[doctor_id] = {
            "doctor_name": doctor.get("name", "Unknown"),
            "specialization": doctor.get("specialization", "Unknown"),
            "appointments": len(doctor_appointments),
            "completed_appointments": len(completed),
            "cancelled_appointments": len(cancelled),
            "total_revenue": revenue,
            "average_bill": average_bill,
        }

    return report


def generate_patient_report(
    patients, doctors, appointments, test_prices, config=None
):
    """Generate appointment and billing statistics for every patient."""
    if not isinstance(patients, dict):
        return {}

    records = _valid_appointments(appointments)
    report = {}

    for patient_id, patient in patients.items():
        if not isinstance(patient, dict):
            continue

        patient_appointments = [
            item for item in records
            if item.get("patient_id") == patient_id
        ]

        completed = [
            item for item in patient_appointments
            if item.get("status") == "completed"
        ]

        cancelled = [
            item for item in patient_appointments
            if item.get("status") == "cancelled"
        ]

        bills = [
            _get_bill(item, patients, doctors, test_prices, config)
            for item in completed
        ]

        bills = [bill for bill in bills if bill is not None]

        report[patient_id] = {
            "patient_name": patient.get("name", "Unknown"),
            "age": patient.get("age"),
            "insurance": patient.get("insurance") is True,
            "appointments": len(patient_appointments),
            "completed_appointments": len(completed),
            "cancelled_appointments": len(cancelled),
            "total_medical_charges": sum(
                bill["subtotal"] for bill in bills
            ),
            "insurance_coverage": sum(
                bill["insurance_coverage"] for bill in bills
            ),
            "patient_paid": sum(
                bill["final_bill"] for bill in bills
            ),
        }

    return report


def generate_clinic_report(
    patients, doctors, appointments, test_prices, config=None
):
    """Generate clinic-wide management statistics."""
    if not isinstance(patients, dict):
        patients = {}

    if not isinstance(doctors, dict):
        doctors = {}

    records = _valid_appointments(appointments)

    doctor_report = generate_doctor_report(
        patients, doctors, records, test_prices, config
    )

    patient_report = generate_patient_report(
        patients, doctors, records, test_prices, config
    )

    completed = [
        item for item in records
        if item.get("status") == "completed"
    ]

    cancelled = [
        item for item in records
        if item.get("status") == "cancelled"
    ]

    pending = [
        item for item in records
        if item.get("status") == "pending"
    ]

    # Calculate each valid completed appointment's bill once.
    completed_bills = [
        _get_bill(item, patients, doctors, test_prices, config)
        for item in completed
    ]

    valid_bills = [
        (appointment, bill)
        for appointment, bill in zip(completed, completed_bills)
        if bill is not None
    ]

    consultation_revenue = sum(
        bill["consultation_fee"] for _, bill in valid_bills
    )

    test_revenue = sum(
        bill["test_charges"] for _, bill in valid_bills
    )

    insurance_total = sum(
        bill["insurance_coverage"] for _, bill in valid_bills
    )

    senior_discount_total = sum(
        bill["senior_discount"] for _, bill in valid_bills
    )

    patient_revenue = sum(
        bill["final_bill"] for _, bill in valid_bills
    )

    patient_revenue = sum(
        bill["final_bill"] for _, bill in valid_bills
    )

    print("Calculated Patient Revenue:", patient_revenue)
    print("--- END DEBUG ---\n")
    # Lambda sorts and identifies the most-requested doctor.
    most_requested_doctor = max(
        doctor_report.items(),
        key=lambda item: item[1]["appointments"],
        default=None,
    )

    specialization_counts = {}

    for appointment in records:
        doctor = doctors.get(appointment.get("doctor_id"), {})

        if not isinstance(doctor, dict):
            continue

        specialization = doctor.get("specialization", "Unknown")

        specialization_counts[specialization] = (
            specialization_counts.get(specialization, 0) + 1
        )

    most_requested_specialization = max(
        specialization_counts.items(),
        key=lambda item: item[1],
        default=None,
    )

    highest_spending_patient = max(
        patient_report.items(),
        key=lambda item: item[1]["patient_paid"],
        default=None,
    )

    patient_with_most_appointments = max(
        patient_report.items(),
        key=lambda item: item[1]["appointments"],
        default=None,
    )

    # Required comprehensions.
    senior_age = (config or {}).get("senior_age", 60)

    insured_patients = [
        patient_id
        for patient_id, patient in patients.items()
        if isinstance(patient, dict)
        and patient.get("insurance") is True
    ]

    senior_patients = [
        patient_id
        for patient_id, patient in patients.items()
        if isinstance(patient, dict)
        and isinstance(patient.get("age"), int)
        and not isinstance(patient.get("age"), bool)
        and patient["age"] >= senior_age
    ]

    patients_without_completed = [
        patient_id
        for patient_id, data in patient_report.items()
        if data["completed_appointments"] == 0
    ]

    return {
        "total_patients": len(patients),
        "total_doctors": len(doctors),
        "total_appointments": len(records),
        "completed": len(completed),
        "cancelled": len(cancelled),
        "pending": len(pending),
        "total_consultation_revenue": consultation_revenue,
        "total_test_revenue": test_revenue,
        "total_insurance_coverage": insurance_total,
        "total_senior_discount": senior_discount_total,
        "total_patient_revenue": patient_revenue,
        "most_requested_doctor": most_requested_doctor,
        "most_requested_specialization": most_requested_specialization,
        "highest_spending_patient": highest_spending_patient,
        "patient_with_most_appointments": patient_with_most_appointments,
        "patients_without_completed_appointment": patients_without_completed,
        "insured_patients": insured_patients,
        "senior_citizen_patients": senior_patients,
        "doctor_report": doctor_report,
        "patient_report": patient_report,
    }


def print_clinic_dashboard(report, currency="$"):
    """Display a readable clinic management dashboard."""
    if not isinstance(report, dict):
        print("Cannot display dashboard: invalid report.")
        return

    print("=" * 48)
    print("              CLINIC DASHBOARD")
    print("=" * 48)

    print(f"Total Patients: {report.get('total_patients', 0)}")
    print(f"Total Doctors: {report.get('total_doctors', 0)}")
    print(f"Total Appointments: {report.get('total_appointments', 0)}")
    print(f"Completed: {report.get('completed', 0)}")
    print(f"Cancelled: {report.get('cancelled', 0)}")
    print(f"Pending: {report.get('pending', 0)}")

    print(
        "Total Consultation Revenue: "
        f"{currency}{report.get('total_consultation_revenue', 0):,.2f}"
    )

    print(
        "Total Test Revenue: "
        f"{currency}{report.get('total_test_revenue', 0):,.2f}"
    )

    print(
        "Total Insurance Coverage: "
        f"{currency}{report.get('total_insurance_coverage', 0):,.2f}"
    )
    print(
        f"Total Senior Citizen Discount: "
        f"{currency}{report['total_senior_discount']:,.2f}"
    )

    print(
        "Total Patient Revenue: "
        f"{currency}{report.get('total_patient_revenue', 0):,.2f}"
    )

    specialization = report.get("most_requested_specialization")

    print(
        "Most Requested Specialization: "
        f"{specialization[0] if specialization else 'N/A'}"
    )

    highest = report.get("highest_spending_patient")

    print(
        "Highest Spending Patient: "
        f"{highest[1]['patient_name'] if highest else 'N/A'}"
    )

    print("=" * 48)
