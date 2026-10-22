"""Command-line interface for the clinic management system."""

import sys
from appointments import process_appointment, cancel_appointment
from billing import calculate_bill
from config import CLINIC_CONFIG
from data import patients, doctors, appointments, test_prices
from reports import (
    generate_clinic_report,
    print_clinic_dashboard,
    generate_doctor_report,
    generate_patient_report,
)
from validation import validate_appointment


def print_menu() -> None:
    """Print the available menu options."""
    print("\n" + "=" * 20 + " CLINIC MANAGEMENT PORTAL " + "=" * 20)
    print("1.  View clinic dashboard")
    print("2.  View patients")
    print("3.  View doctors")
    print("4.  View appointments")
    print("5.  Process an appointment")
    print("6.  Cancel an appointment")
    print("7.  Create a sample bill")
    print("8.  View doctor report")
    print("9.  View patient report")
    print("10. Book an appointment")
    print("0.  Exit")
    print("=" * 66)


def display_patients() -> None:
    """Print all patient records."""
    print("\n--- PATIENTS ---")
    for pid, details in patients.items():
        print(
            f"ID: {pid} | Name: {details.get('name')} | Age: {details.get('age')} | City: {details.get('city')} | Insured: {details.get('insurance')}")


def display_doctors() -> None:
    """Print all doctor records."""
    print("\n--- DOCTORS ---")
    for doc_id, details in doctors.items():
        print(
            f"ID: {doc_id} | Name: {details.get('name')} | Specialization: {details.get('specialization')} | Base Fee: {details.get('fee')} | Available: {details.get('available')}")


def display_appointments() -> None:
    """Print all appointments."""
    print("\n--- APPOINTMENTS ---")
    for app in appointments:
        tests_list = ", ".join(app.get("tests", [])) or "None"
        print(
            f"App-ID: {app.get('appointment_id')} | Patient-ID: {app.get('patient_id')} | Doctor-ID: {app.get('doctor_id')} | Status: {app.get('status')} | Tests: {tests_list}")


def handle_process_appointment() -> None:
    """Process a pending appointment."""
    app_id = input("Enter Appointment ID to process: ").strip()
    result = process_appointment(app_id, patients, doctors, appointments, test_prices, CLINIC_CONFIG)
    if isinstance(result, tuple) and not result[0]:
        print(f"Operation Failed: {result[1]}")
    else:
        print(f"Appointment {app_id} processed.")


def handle_cancel_appointment() -> None:
    """Cancel a pending appointment."""
    app_id = input("Enter Appointment ID to cancel: ").strip()
    result = cancel_appointment(app_id, appointments)
    if not result[0]:
        print(f"Cancellation Refused: {result[1]}")
    else:
        print(f"Appointment {app_id} cancelled.")


def handle_sample_bill() -> None:
    """Create and print a sample bill."""
    print("\n--- SAMPLE BILL ---")
    pid = input("Enter patient ID: ").strip()
    did = input("Enter doctor ID: ").strip()
    if pid not in patients or did not in doctors:
        print("Patient or doctor not found.")
        return
    selected_tests = input(
        "Enter test names separated by commas (or leave blank): "
    ).strip()
    tests = [test.strip() for test in selected_tests.split(",") if test.strip()]
    patient = patients[pid]
    doctor = doctors[did]
    result = calculate_bill(
        doctor["fee"],
        tests,
        test_prices,
        patient["age"],
        insurance=patient["insurance"],
        config=CLINIC_CONFIG,
    )
    if not result[0]:
        print(f"Could not create bill: {result[1]}")
        return

    bill = result[1]
    currency = bill["currency"]
    print(f"Consultation fee: {currency}{bill['consultation_fee']:,.2f}")
    print(f"Test charges: {currency}{bill['test_charges']:,.2f}")
    print(f"Subtotal: {currency}{bill['subtotal']:,.2f}")
    print(f"Insurance coverage: {currency}{bill['insurance_coverage']:,.2f}")
    print(f"Senior discount: {currency}{bill['senior_discount']:,.2f}")
    print(f"Final bill: {currency}{bill['final_bill']:,.2f}")


def handle_doctor_report() -> None:
    """Print a report for each doctor."""
    doc_report = generate_doctor_report(patients, doctors, appointments, test_prices, CLINIC_CONFIG)
    print("\n--- DOCTOR REPORT ---")
    print(doc_report)


def handle_patient_report() -> None:
    """Print appointment history for each patient."""
    pat_report = generate_patient_report(patients, doctors, appointments, test_prices, CLINIC_CONFIG)
    print("\n--- PATIENT REPORT ---")
    print(pat_report)


def handle_add_appointment() -> None:
    """Book an appointment after validating its details."""
    print("\n--- BOOK AN APPOINTMENT ---")
    app_id = input("Enter appointment ID (e.g., A005): ").strip()
    pid = input("Enter Patient ID: ").strip()
    did = input("Enter Doctor ID: ").strip()

    new_app = {
        "appointment_id": app_id,
        "patient_id": pid,
        "doctor_id": did,
        "status": "pending",
        "tests": []
    }

    validation_status = validate_appointment(
        new_app,
        patients,
        doctors,
        test_prices,
        appointments,
    )
    if not validation_status[0]:
        print(f"Could not book appointment: {validation_status[1]}")
    else:
        appointments.append(new_app)
        print(f"Appointment {app_id} added.")


def main() -> None:
    """Run the clinic management menu."""
    while True:
        try:
            print_menu()
            choice = input("Select an option: ").strip()

            if choice == "1":
                report = generate_clinic_report(
                    patients,
                    doctors,
                    appointments,
                    test_prices,
                    CLINIC_CONFIG,
                )
                print_clinic_dashboard(report)

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
                print("Exiting application. Goodbye!")
                sys.exit(0)

            else:
                print("Invalid option. Please try again.")

        except (KeyboardInterrupt, EOFError):
            print("\n\nSession closed. Goodbye!")
            sys.exit(0)


if __name__ == "__main__":
    main()