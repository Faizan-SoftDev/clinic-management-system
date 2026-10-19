"""Command-line Clinic Management System."""

from data import patients, doctors, appointments, test_prices
from config import CLINIC_CONFIG
from appointments import find_appointment, process_appointment, cancel_appointment
from billing import calculate_bill
from reports import (
    generate_doctor_report,
    generate_patient_report,
    generate_clinic_report,
    print_clinic_dashboard,
)
from validation import validate_appointment


def print_menu():
    """Display the application's main menu."""
    print("\n" + "=" * 48)
    print("          CLINIC MANAGEMENT SYSTEM")
    print("=" * 48)
    print("1. View clinic dashboard")
    print("2. View patients")
    print("3. View doctors")
    print("4. View appointments")
    print("5. Process appointment")
    print("6. Cancel appointment")
    print("7. Calculate a sample bill")
    print("8. View doctor report")
    print("9. View patient report")
    print("10. Add pending appointment")
    print("0. Exit")
    print("=" * 48)


def display_patients():
    """Display all registered patients."""
    if not patients:
        print("No patients registered.")
        return

    print("\nREGISTERED PATIENTS")

    for patient_id, patient in patients.items():
        if not isinstance(patient, dict):
            continue

        print(
            f"{patient_id} | "
            f"Name: {patient.get('name', 'Unknown')} | "
            f"Age: {patient.get('age', 'Unknown')} | "
            f"City: {patient.get('city', 'Unknown')} | "
            f"Insurance: {patient.get('insurance', False)}"
        )


def display_doctors():
    """Display all registered doctors."""
    if not doctors:
        print("No doctors registered.")
        return

    print("\nREGISTERED DOCTORS")

    for doctor_id, doctor in doctors.items():
        if not isinstance(doctor, dict):
            continue

        print(
            f"{doctor_id} | "
            f"Name: {doctor.get('name', 'Unknown')} | "
            f"Specialization: {doctor.get('specialization', 'Unknown')} | "
            f"Fee: {CLINIC_CONFIG['currency']}{doctor.get('fee', 0)} | "
            f"Available: {doctor.get('available', False)}"
        )


def display_appointments():
    """Display all appointments and their current statuses."""
    if not appointments:
        print("No appointments registered.")
        return

    print("\nAPPOINTMENTS")

    for appointment in appointments:
        if not isinstance(appointment, dict):
            continue

        print(
            f"{appointment.get('appointment_id', 'Unknown')} | "
            f"Patient: {appointment.get('patient_id', 'Unknown')} | "
            f"Doctor: {appointment.get('doctor_id', 'Unknown')} | "
            f"Status: {appointment.get('status', 'Unknown')} | "
            f"Tests: {appointment.get('tests', [])}"
        )


def handle_process_appointment():
    """Ask for an appointment ID and process the appointment."""
    appointment_id = input("Enter appointment ID: ").strip()

    success, result = process_appointment(
        appointment_id,
        patients,
        doctors,
        appointments,
        test_prices,
        CLINIC_CONFIG,
    )

    if not success:
        print(f"REJECTED | Reason: {result}")
        return

    print(result["message"])
    print(f"Patient: {result['patient_name']}")
    print(f"Doctor: {result['doctor_name']}")

    bill = result["bill"]
    currency = bill["currency"]

    print("\nBILL DETAILS")
    print(f"Consultation fee: {currency}{bill['consultation_fee']:,.2f}")
    print(f"Test charges: {currency}{bill['test_charges']:,.2f}")
    print(f"Subtotal: {currency}{bill['subtotal']:,.2f}")
    print(f"Insurance coverage: {currency}{bill['insurance_coverage']:,.2f}")
    print(f"Senior discount: {currency}{bill['senior_discount']:,.2f}")
    print(f"Final bill: {currency}{bill['final_bill']:,.2f}")


def handle_cancel_appointment():
    """Ask for an appointment ID and cancel it if permitted."""
    appointment_id = input("Enter appointment ID to cancel: ").strip()

    success, message = cancel_appointment(appointment_id, appointments)

    if success:
        print(f"SUCCESS | {message}")
    else:
        print(f"REJECTED | Reason: {message}")


def handle_sample_bill():
    """Calculate a bill using patient and doctor records."""
    patient_id = input("Enter patient ID: ").strip()
    doctor_id = input("Enter doctor ID: ").strip()

    if patient_id not in patients:
        print(f"REJECTED | Patient {patient_id} does not exist.")
        return

    if doctor_id not in doctors:
        print(f"REJECTED | Doctor {doctor_id} does not exist.")
        return

    patient = patients[patient_id]
    doctor = doctors[doctor_id]

    if not isinstance(patient, dict) or not isinstance(doctor, dict):
        print("REJECTED | Patient or doctor data is invalid.")
        return

    if (
        isinstance(patient.get("age"), bool)
        or not isinstance(patient.get("age"), int)
        or patient["age"] < 0
    ):
        print("REJECTED | Patient age is invalid.")
        return

    if patient.get("insurance") not in (True, False):
        print("REJECTED | Patient insurance data is invalid.")
        return

    result = calculate_bill(
        doctor.get("fee"),
        [],
        test_prices,
        patient["age"],
        insurance=patient["insurance"],
        senior_discount=True,
        include_tests=False,
        config=CLINIC_CONFIG,
    )

    if not result[0]:
        print(f"REJECTED | Reason: {result[1]}")
        return

    bill = result[1]
    currency = bill["currency"]

    print("\nSAMPLE BILL")
    print(f"Patient: {patient['name']}")
    print(f"Doctor: {doctor['name']}")
    print(f"Consultation fee: {currency}{bill['consultation_fee']:,.2f}")
    print(f"Insurance coverage: {currency}{bill['insurance_coverage']:,.2f}")
    print(f"Senior discount: {currency}{bill['senior_discount']:,.2f}")
    print(f"Final amount: {currency}{bill['final_bill']:,.2f}")
    print("Note: This is a calculation only; no appointment was processed.")


def handle_doctor_report():
    """Display statistics for each doctor."""
    report = generate_doctor_report(
        patients, doctors, appointments, test_prices, CLINIC_CONFIG
    )

    if not report:
        print("No doctor report data available.")
        return

    print("\nDOCTOR REPORT")

    for doctor_id, details in report.items():
        print(f"\n{doctor_id} | {details['doctor_name']}")
        print(f"Specialization: {details['specialization']}")
        print(f"Appointments: {details['appointments']}")
        print(f"Completed: {details['completed_appointments']}")
        print(f"Cancelled: {details['cancelled_appointments']}")
        print(f"Revenue: {CLINIC_CONFIG['currency']}{details['total_revenue']:,.2f}")
        print(f"Average bill: {CLINIC_CONFIG['currency']}{details['average_bill']:,.2f}")


def handle_patient_report():
    """Display statistics for each patient."""
    report = generate_patient_report(
        patients, doctors, appointments, test_prices, CLINIC_CONFIG
    )

    if not report:
        print("No patient report data available.")
        return

    print("\nPATIENT REPORT")

    for patient_id, details in report.items():
        print(f"\n{patient_id} | {details['patient_name']}")
        print(f"Insurance: {details['insurance']}")
        print(f"Appointments: {details['appointments']}")
        print(f"Completed: {details['completed_appointments']}")
        print(f"Cancelled: {details['cancelled_appointments']}")
        print(
            "Medical charges: "
            f"{CLINIC_CONFIG['currency']}{details['total_medical_charges']:,.2f}"
        )
        print(
            "Insurance coverage: "
            f"{CLINIC_CONFIG['currency']}{details['insurance_coverage']:,.2f}"
        )
        print(
            "Patient paid: "
            f"{CLINIC_CONFIG['currency']}{details['patient_paid']:,.2f}"
        )


def handle_add_appointment():
    """Create a new pending appointment after validating its details."""
    appointment_id = input("New appointment ID: ").strip()
    patient_id = input("Patient ID: ").strip()
    doctor_id = input("Doctor ID: ").strip()
    tests_input = input(
        "Medical tests separated by commas (leave empty for none): "
    ).strip()

    if not appointment_id:
        print("REJECTED | Appointment ID cannot be empty.")
        return

    if find_appointment(appointment_id, appointments) is not None:
        print(f"REJECTED | Appointment {appointment_id} already exists.")
        return

    if patient_id not in patients:
        print(f"REJECTED | Patient {patient_id} does not exist.")
        return

    if doctor_id not in doctors:
        print(f"REJECTED | Doctor {doctor_id} does not exist.")
        return

    if not isinstance(patients[patient_id], dict):
        print(f"REJECTED | Patient {patient_id} has invalid data.")
        return

    if not isinstance(doctors[doctor_id], dict):
        print(f"REJECTED | Doctor {doctor_id} has invalid data.")
        return

    tests = [
        test.strip()
        for test in tests_input.split(",")
        if test.strip()
    ]

    new_appointment = {
        "appointment_id": appointment_id,
        "patient_id": patient_id,
        "doctor_id": doctor_id,
        "status": "pending",
        "tests": tests,
    }

    # Validate the complete appointment before changing the records.
    result = validate_appointment(
        new_appointment, patients, doctors, test_prices
    )

    if not result[0]:
        print(f"REJECTED | Reason: {result[1]}")
        return

    appointments.append(new_appointment)

    print(f"SUCCESS | Appointment {appointment_id} created as pending.")


def main():
    """Run the clinic management menu."""
    print("Welcome to the Clinic Management System")

    while True:
        print_menu()

        choice = input("Choose an option: ").strip()

        if choice == "1":
            report = generate_clinic_report(
                patients, doctors, appointments, test_prices, CLINIC_CONFIG
            )
            print_clinic_dashboard(report, CLINIC_CONFIG["currency"])

        elif choice == "2":
            display_patients()

        elif choice == "3":
            display_doctors()

        elif choice == "4":
            display_appointments()

        elif choice == "5":
            handle_process_appointment()

        elif choice == "6":
            handle_cancel_appointment()

        elif choice == "7":
            handle_sample_bill()

        elif choice == "8":
            handle_doctor_report()

        elif choice == "9":
            handle_patient_report()

        elif choice == "10":
            handle_add_appointment()

        elif choice == "0":
            print("Thank you for using the Clinic Management System.")
            break

        else:
            print("Invalid option. Please select a number from 0 to 10.")


def run():
    """Start the application and handle normal terminal interruptions."""
    try:
        main()
    except (EOFError, KeyboardInterrupt):
        print("\nClinic Management System closed.")


if __name__ == "__main__":
    run()
