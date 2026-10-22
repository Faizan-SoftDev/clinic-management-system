"""Reporting and analytics for the Clinic Management System using lambdas and comprehensions."""

from typing import Dict, Any, List


def generate_doctor_report(
    patients: Dict[str, Any],
    doctors: Dict[str, Any],
    appointments: List[Dict[str, Any]],
    test_prices: Dict[str, float],
    config: Dict[str, Any],
) -> str:
    """Generate analytical performance report for all doctors."""
    if not isinstance(doctors, dict) or not doctors:
        return "No doctor records available."

    report_lines = ["\n--- DOCTOR PERFORMANCE METRICS ---"]

    doc_stats = {}
    for did, doc_info in doctors.items():
        doc_apps = [a for a in appointments if isinstance(a, dict) and a.get("doctor_id") == did]
        completed_apps = [a for a in doc_apps if a.get("status") == "completed"]
        cancelled_apps = [a for a in doc_apps if a.get("status") == "cancelled"]

        total_revenue = sum(
            a.get("bill", {}).get("final_bill", 0.0)
            for a in completed_apps
            if isinstance(a.get("bill"), dict)
        )
        avg_bill = (total_revenue / len(completed_apps)) if completed_apps else 0.0

        doc_stats[did] = {
            "name": doc_info.get("name", "Unknown"),
            "specialization": doc_info.get("specialization", "General"),
            "total_appointments": len(doc_apps),
            "completed": len(completed_apps),
            "cancelled": len(cancelled_apps),
            "revenue": total_revenue,
            "avg_bill": avg_bill,
        }

    currency = config.get("currency", "$")

    for did, stats in doc_stats.items():
        report_lines.append(
            f"Doctor ID: {did} | Name: {stats['name']} ({stats['specialization']}) | "
            f"Total Apps: {stats['total_appointments']} | Completed: {stats['completed']} | "
            f"Cancelled: {stats['cancelled']} | Revenue: {currency}{stats['revenue']:,.2f} | "
            f"Avg Bill: {currency}{stats['avg_bill']:,.2f}"
        )

    sorted_doctors = sorted(
        doc_stats.items(),
        key=lambda item: item[1]["revenue"],
        reverse=True,
    )

    if sorted_doctors:
        top_doc = sorted_doctors[0]
        report_lines.append(f"\nTop Revenue Doctor: {top_doc[1]['name']} ({currency}{top_doc[1]['revenue']:,.2f})")

    return "\n".join(report_lines)


def generate_patient_report(
    patients: Dict[str, Any],
    doctors: Dict[str, Any],
    appointments: List[Dict[str, Any]],
    test_prices: Dict[str, float],
    config: Dict[str, Any],
) -> str:
    """Generate patient history metrics and analytics."""
    if not isinstance(patients, dict) or not patients:
        return "No patient records available."

    report_lines = ["\n--- PATIENT HISTORY METRICS ---"]
    currency = config.get("currency", "$")

    patient_stats = {}
    for pid, p_info in patients.items():
        p_apps = [a for a in appointments if isinstance(a, dict) and a.get("patient_id") == pid]
        completed = [a for a in p_apps if a.get("status") == "completed"]
        cancelled = [a for a in p_apps if a.get("status") == "cancelled"]

        total_spent = sum(
            a.get("bill", {}).get("final_bill", 0.0)
            for a in completed
            if isinstance(a.get("bill"), dict)
        )
        total_insurance = sum(
            a.get("bill", {}).get("insurance_coverage", 0.0)
            for a in completed
            if isinstance(a.get("bill"), dict)
        )

        patient_stats[pid] = {
            "name": p_info.get("name", "Unknown"),
            "total_apps": len(p_apps),
            "completed": len(completed),
            "cancelled": len(cancelled),
            "total_spent": total_spent,
            "insurance_coverage": total_insurance,
            "insurance_enabled": p_info.get("insurance", False),
            "age": p_info.get("age", 0),
        }

    for pid, stats in patient_stats.items():
        report_lines.append(
            f"Patient ID: {pid} | Name: {stats['name']} | Apps: {stats['total_apps']} "
            f"(Done: {stats['completed']}, Cancelled: {stats['cancelled']}) | "
            f"Spent: {currency}{stats['total_spent']:,.2f} | Covered: {currency}{stats['insurance_coverage']:,.2f}"
        )

    insured_patients = [p["name"] for p in patients.values() if p.get("insurance") is True]
    senior_patients = [p["name"] for p in patients.values() if p.get("age", 0) >= config.get("senior_age", 60)]
    no_completed_apps = [
        stats["name"] for pid, stats in patient_stats.items() if stats["completed"] == 0
    ]

    report_lines.append(f"\nInsured Patients: {', '.join(insured_patients) or 'None'}")
    report_lines.append(f"Senior Citizens: {', '.join(senior_patients) or 'None'}")
    report_lines.append(f"Patients with No Completed Appointments: {', '.join(no_completed_apps) or 'None'}")

    highest_spender = max(
        patient_stats.items(),
        key=lambda item: item[1]["total_spent"],
        default=(None, {"name": "None", "total_spent": 0}),
    )
    report_lines.append(f"Highest Spending Patient: {highest_spender[1]['name']} ({currency}{highest_spender[1]['total_spent']:,.2f})")

    return "\n".join(report_lines)


def generate_clinic_report(
    patients: Dict[str, Any],
    doctors: Dict[str, Any],
    appointments: List[Dict[str, Any]],
    test_prices: Dict[str, float],
    config: Dict[str, Any],
) -> Dict[str, Any]:
    """Compile aggregated metrics for the clinic management dashboard."""
    total_patients = len(patients)
    total_doctors = len(doctors)
    total_appointments = len(appointments)

    completed_count = sum(1 for a in appointments if isinstance(a, dict) and a.get("status") == "completed")
    cancelled_count = sum(1 for a in appointments if isinstance(a, dict) and a.get("status") == "cancelled")
    pending_count = sum(1 for a in appointments if isinstance(a, dict) and a.get("status") == "pending")

    total_consultation_rev = 0.0
    total_test_rev = 0.0
    total_insurance_cov = 0.0
    total_senior_discounts = 0.0
    total_patient_rev = 0.0
    completed_without_bill_count = 0

    for a in appointments:
        if not isinstance(a, dict) or a.get("status") != "completed":
            continue
        bill = a.get("bill")
        if not isinstance(bill, dict) or not bill:
            completed_without_bill_count += 1
            continue

        total_consultation_rev += bill.get("consultation_fee", 0.0) - bill.get("consultation_coverage", 0.0)
        total_test_rev += bill.get("test_charges", 0.0) - bill.get("test_coverage", 0.0)
        total_insurance_cov += bill.get("insurance_coverage", 0.0)
        total_senior_discounts += bill.get("senior_discount", 0.0)
        total_patient_rev += bill.get("final_bill", 0.0)

    spec_counts = {}
    for a in appointments:
        if not isinstance(a, dict):
            continue
        did = a.get("doctor_id")
        if did in doctors:
            spec = doctors[did].get("specialization", "General")
            spec_counts[spec] = spec_counts.get(spec, 0) + 1

    most_requested_spec = max(
        spec_counts.items(),
        key=lambda item: item[1],
        default=("None", 0),
    )[0]

    patient_spend = {}
    for a in appointments:
        if not isinstance(a, dict) or a.get("status") != "completed":
            continue
        pid = a.get("patient_id")
        bill = a.get("bill")
        if isinstance(bill, dict):
            bill_amt = bill.get("final_bill", 0.0)
            patient_spend[pid] = patient_spend.get(pid, 0.0) + bill_amt

    highest_spender_id = max(
        patient_spend.items(),
        key=lambda item: item[1],
        default=(None, 0),
    )[0]
    highest_spender_name = patients.get(highest_spender_id, {}).get("name", "None") if highest_spender_id else "None"

    currency = config.get("currency", "$")

    return {
        "total_patients": total_patients,
        "total_doctors": total_doctors,
        "total_appointments": total_appointments,
        "completed": completed_count,
        "cancelled": cancelled_count,
        "pending": pending_count,
        "consultation_revenue": total_consultation_rev,
        "test_revenue": total_test_rev,
        "insurance_coverage": total_insurance_cov,
        "senior_discounts": total_senior_discounts,
        "patient_revenue": total_patient_rev,
        "completed_without_bill_count": completed_without_bill_count,
        "most_requested_specialization": most_requested_spec,
        "highest_spending_patient": highest_spender_name,
        "currency": currency,
    }


def print_clinic_dashboard(report: Dict[str, Any]) -> None:
    """Print the formatted clinic management dashboard with complete metrics."""
    curr = report.get("currency", "$")
    print("\n" + "=" * 40)
    print("           CLINIC DASHBOARD")
    print("=" * 40)
    print(f"Total Patients: {report.get('total_patients', 0)}")
    print(f"Total Doctors: {report.get('total_doctors', 0)}")
    print(f"Total Appointments: {report.get('total_appointments', 0)}")
    print(f"Completed: {report.get('completed', 0)}")
    print(f"Cancelled: {report.get('cancelled', 0)}")
    print(f"Pending: {report.get('pending', 0)}")
    print(f"Total Consultation Revenue: {curr}{report.get('consultation_revenue', 0):,.2f}")
    print(f"Total Test Revenue: {curr}{report.get('test_revenue', 0):,.2f}")
    print(f"Total Insurance Coverage: {curr}{report.get('insurance_coverage', 0):,.2f}")
    print(f"Total Senior Discounts: {curr}{report.get('senior_discounts', 0):,.2f}")
    print(f"Total Patient Revenue: {curr}{report.get('patient_revenue', 0):,.2f}")
    missing_bill_count = report.get("completed_without_bill_count", 0)
    if missing_bill_count:
        appointment_word = "appointment" if missing_bill_count == 1 else "appointments"
        verb = "has" if missing_bill_count == 1 else "have"
        print(
            f"Warning: {missing_bill_count} completed {appointment_word} "
            f"{verb} no bill."
        )
    print(
        "Most Requested Specialization: "
        f"{report.get('most_requested_specialization', 'None')}"
    )
    print(f"Highest Spending Patient: {report.get('highest_spending_patient', 'None')}")
    print("=" * 40)