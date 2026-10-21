"""Main execution application engine control loop for the Clinic Management System."""

import sys
from config import CLINIC_CONFIG
from data import patients, doctors, appointments, test_prices
from reports import generate_clinic_report, print_clinic_dashboard, generate_doctor_report, generate_patient_report
from appointments import process_appointment, cancel_appointment, find_appointment


def print_menu() -> None:
    """Render the dashboard interactive choice control grid."""
    print("\n" + "=" * 20 + " CLINIC MANAGEMENT PORTAL " + "=" * 20)
    print("1.  Generate & Print Clinic Dashboard Report")
    print("2.  View All Registered Patients Profiles")
    print("3.  View Medical Roster / Doctors List")
    print("4.  View Global Appointments Schedule Logs")
    print("5.  Process Pending Appointment Status")
    print("6.  Cancel Scheduled Active Appointment")
    print("7.  Simulate Sample Patient Invoice Bill")
    print("8.  Generate Individual Doctor Performance Report")
    print("9.  Generate Detailed Patient History Metrics")
    print("10. Add / Book New Appointment Log")
    print("0.  Exit System and Safely Close Session")
    print("=" * 66)


def display_patients() -> None:
    """Print complete details of all current active patient nodes."""
    print("\n--- REGISTERED PATIENTS SYSTEM RECORDS ---")
    for pid, details in patients.items():
        print(
            f"ID: {pid} | Name: {details.get('name')} | Age: {details.get('age')} | City: {details.get('city')} | Insured: {details.get('insurance')}")


def display_doctors() -> None:
    """Print the complete clinical medical team specifications."""
    print("\n--- ACTIVE MEDICAL STAFF ROSTER ---")
    for doc_id, details in doctors.items():
        print(
            f"ID: {doc_id} | Name: {details.get('name')} | Specialization: {details.get('specialization')} | Base Fee: {details.get('fee')} | Available: {details.get('available')}")


def display_appointments() -> None:
    """List out chronologically scheduled event registries."""
    print("\n--- SCHEDULED CLINIC APPOINTMENTS LOGS ---")
    for app in appointments:
        tests_list = ", ".join(app.get("tests", [])) or "None"
        print(
            f"App-ID: {app.get('appointment_id')} | Patient-ID: {app.get('patient_id')} | Doctor-ID: {app.get('doctor_id')} | Status: {app.get('status')} | Tests: {tests_list}")


def handle_process_appointment() -> None:
    """Workflow handler to transition pending queues to completed invoices."""
    app_id = input("Enter Appointment ID to process: ").strip()
    result = process_appointment(app_id, patients, doctors, appointments, test_prices, CLINIC_CONFIG)
    if isinstance(result, tuple) and not result[0]:
        print(f"Operation Failed: {result[1]}")
    else:
        print(f"Success: Appointment {app_id} successfully converted to historical invoice logs.")


def handle_cancel_appointment() -> None:
    """Transition scheduled queues securely to cancelled state files."""
    app_id = input("Enter Appointment ID to cancel: ").strip()
    result = cancel_appointment(app_id, appointments)
    if not result[0]:
        print(f"Cancellation Refused: {result[1]}")
    else:
        print(f"Success: Appointment {app_id} status updated to cancelled registry parameters.")


def handle_sample_bill() -> None:
    """Simulate test invoicing arrays on current staging entries."""
    from billing import calculate_bill
    print("\n--- SIMULATE PATIENT BILL INVOICE ---")
    pid = input("Enter target Patient ID: ").strip()
    did = input("Enter assigned Doctor ID: ").strip()
    if pid not in patients or did not in doctors:
        print("Invalid operational keys provided. Simulation halted.")
        return
    patient = patients[pid]
    doctor = doctors[did]
    result = calculate_bill(doctor["fee"], [], test_prices, patient["age"], insurance=patient["insurance"])
    print(f"Simulated Matrix Output Invoice Details: {result}")


def handle_doctor_report() -> None:
    """Compile specific operational doctor summaries across data stores."""
    doc_report = generate_doctor_report(patients, doctors, appointments, test_prices, CLINIC_CONFIG)
    print("\n--- COMPILED DOCTORS ANALYTICS LEDGER ---")
    print(doc_report)


def handle_patient_report() -> None:
    """Compile historical treatment patient grids safely."""
    pat_report = generate_patient_report(patients, doctors, appointments, test_prices, CLINIC_CONFIG)
    print("\n--- COMPILED PATIENTS LOGISTICAL HISTORY ---")
    print(pat_report)


def handle_add_appointment() -> None:
    """Book a new entry while running strict validation checks against duplicates."""
    from validation import validate_appointment
    print("\n--- SCHEDULING NEW ACTIVE APPOINTMENT ---")
    app_id = input("Generate New Unique App ID (e.g., A005): ").strip()

    if find_appointment(app_id, appointments) is not None:
        print(f"Booking Denied: Appointment ID {app_id} already exists.")
        return

    pid = input("Enter Patient ID: ").strip()
    did = input("Enter Doctor ID: ").strip()

    new_app = {
        "appointment_id": app_id,
        "patient_id": pid,
        "doctor_id": did,
        "status": "pending",
        "tests": []
    }

    validation_status = validate_appointment(new_app, patients, doctors, test_prices)
    if not validation_status[0]:
        print(f"Booking Denied: {validation_status[1]}")
    else:
        appointments.append(new_app)
        print(f"Success: Appointment {app_id} safely queued to memory grid pipelines.")


def main() -> None:
    """Main execution application engine control loop."""
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
            print(
                "\n\nSession safely closed via console shortcut signal. "
                "Goodbye!"
            )
            sys.exit(0)


if __name__ == "__main__":
    main()