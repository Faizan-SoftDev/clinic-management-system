"""Reporting module for Clinic Management System."""

from typing import Dict, List, Any


def generate_doctor_report(
    patients: Dict[str, Any],
    doctors: Dict[str, Any],
    appointments: List[Dict[str, Any]],
    test_prices: Dict[str, float],
    config: Dict[str, Any] = None,
) -> Dict[str, Any]:
    """Generate doctor performance metrics strictly honoring historical bill records."""
    doc_stats = {}

    for doc_id, doc in doctors.items():
        doc_apps = [a for a in appointments if isinstance(a, dict) and a.get("doctor_id") == doc_id]
        completed = [a for a in doc_apps if a.get("status") == "completed"]
        cancelled = [a for a in doc_apps if a.get("status") == "cancelled"]

        total_rev = sum(
            a["bill"]["final_bill"]
            for a in completed
            if isinstance(a.get("bill"), dict) and "final_bill" in a["bill"]
        )
        avg_bill = (total_rev / len(completed)) if completed else 0.0

        doc_stats[doc_id] = {
            "name": doc.get("name", "N/A"),
            "specialization": doc.get("specialization", "N/A"),
            "total_appointments": len(doc_apps),
            "completed": len(completed),
            "cancelled": len(cancelled),
            "total_revenue": float(total_rev),
            "average_bill": float(avg_bill),
        }

    most_req_doc = (
        max(doc_stats.values(), key=lambda d: d["total_appointments"])["name"]
        if doc_stats
        else "N/A"
    )

    spec_counts = {}
    for app in appointments:
        if isinstance(app, dict) and app.get("doctor_id") in doctors:
            spec = doctors[app["doctor_id"]].get("specialization", "N/A")
            spec_counts[spec] = spec_counts.get(spec, 0) + 1

    most_req_spec = (
        max(spec_counts.items(), key=lambda x: x[1])[0]
        if spec_counts
        else "N/A"
    )

    return {
        "doctor_statistics": doc_stats,
        "most_requested_doctor": most_req_doc,
        "most_requested_specialization": most_req_spec,
    }


def generate_patient_report(
    patients: Dict[str, Any],
    doctors: Dict[str, Any],
    appointments: List[Dict[str, Any]],
    test_prices: Dict[str, float],
    config: Dict[str, Any] = None,
) -> Dict[str, Any]:
    """Generate patient financial and visit metrics strictly honoring historical bill records."""
    insured_patients = [p["name"] for p in patients.values() if isinstance(p, dict) and p.get("insurance")]
    senior_patients = [
        p["name"]
        for p in patients.values()
        if isinstance(p, dict) and isinstance(p.get("age"), int) and p.get("age") >= 60
    ]

    patient_stats = {}
    for pid, pdata in patients.items():
        p_apps = [a for a in appointments if isinstance(a, dict) and a.get("patient_id") == pid]
        completed = [a for a in p_apps if a.get("status") == "completed"]
        cancelled = [a for a in p_apps if a.get("status") == "cancelled"]

        tot_charges = sum(
            a["bill"]["subtotal"]
            for a in completed
            if isinstance(a.get("bill"), dict) and "subtotal" in a["bill"]
        )
        tot_insurance = sum(
            a["bill"]["insurance_coverage"]
            for a in completed
            if isinstance(a.get("bill"), dict) and "insurance_coverage" in a["bill"]
        )
        tot_paid = sum(
            a["bill"]["final_bill"]
            for a in completed
            if isinstance(a.get("bill"), dict) and "final_bill" in a["bill"]
        )

        patient_stats[pid] = {
            "name": pdata.get("name", "N/A"),
            "total_appointments": len(p_apps),
            "completed": len(completed),
            "cancelled": len(cancelled),
            "total_medical_charges": float(tot_charges),
            "insurance_coverage": float(tot_insurance),
            "patient_paid_amount": float(tot_paid),
        }

    no_completed = [p["name"] for p in patient_stats.values() if p["completed"] == 0]
    highest_spending = (
        max(patient_stats.values(), key=lambda p: p["patient_paid_amount"])["name"]
        if patient_stats
        else "N/A"
    )
    most_apps = (
        max(patient_stats.values(), key=lambda p: p["total_appointments"])["name"]
        if patient_stats
        else "N/A"
    )

    return {
        "patient_statistics": patient_stats,
        "insured_patients": insured_patients,
        "senior_patients": senior_patients,
        "no_completed_appointments": no_completed,
        "highest_spending_patient": highest_spending,
        "patient_with_most_appointments": most_apps,
    }


def generate_clinic_report(
    patients: Dict[str, Any],
    doctors: Dict[str, Any],
    appointments: List[Dict[str, Any]],
    test_prices: Dict[str, float],
    config: Dict[str, Any] = None,
) -> Dict[str, Any]:
    """Generate clinic-wide revenue and operational metrics."""
    tot_patients = len(patients) if patients else 0
    tot_doctors = len(doctors) if doctors else 0
    tot_appointments = len(appointments) if appointments else 0

    completed = len([a for a in appointments if isinstance(a, dict) and a.get("status") == "completed"])
    cancelled = len([a for a in appointments if isinstance(a, dict) and a.get("status") == "cancelled"])
    pending = len([a for a in appointments if isinstance(a, dict) and a.get("status") == "pending"])

    tot_consult_rev = 0.0
    tot_test_rev = 0.0
    tot_insurance = 0.0
    tot_senior_disc = 0.0
    tot_patient_rev = 0.0
    completed_without_bill = 0

    for app in appointments:
        if isinstance(app, dict) and app.get("status") == "completed":
            if "bill" in app and isinstance(app["bill"], dict):
                b = app["bill"]
                c_fee = float(b.get("consultation_fee", 0.0))
                t_fee = float(b.get("test_charges", 0.0))
                c_cov = float(b.get("consultation_coverage", 0.0))
                t_cov = float(b.get("test_coverage", 0.0))

                tot_consult_rev += (c_fee - c_cov)
                tot_test_rev += (t_fee - t_cov)

                tot_insurance += float(b.get("insurance_coverage", 0.0))
                tot_senior_disc += float(b.get("senior_discount", 0.0))
                tot_patient_rev += float(b.get("final_bill", 0.0))
            else:
                completed_without_bill += 1

    doc_rep = generate_doctor_report(patients, doctors, appointments, test_prices, config) if doctors else {}
    pat_rep = generate_patient_report(patients, doctors, appointments, test_prices, config) if patients else {}

    return {
        "total_patients": tot_patients,
        "total_doctors": tot_doctors,
        "total_appointments": tot_appointments,
        "completed": completed,
        "cancelled": cancelled,
        "pending": pending,
        "consultation_revenue": tot_consult_rev,
        "test_revenue": tot_test_rev,
        "insurance_coverage": tot_insurance,
        "senior_discounts": tot_senior_disc,
        "patient_revenue": tot_patient_rev,
        "completed_without_bill_count": completed_without_bill,
        "most_requested_specialization": doc_rep.get("most_requested_specialization", "N/A"),
        "highest_spending_patient": pat_rep.get("highest_spending_patient", "N/A"),
    }


def print_clinic_dashboard(report: Dict[str, Any]) -> None:
    """Print formatted clinic dashboard."""
    if not isinstance(report, dict):
        report = {}

    tot_p = report.get("total_patients", 0)
    tot_d = report.get("total_doctors", 0)
    tot_a = report.get("total_appointments", 0)
    comp = report.get("completed", 0)
    canc = report.get("cancelled", 0)
    pend = report.get("pending", 0)

    c_rev = report.get("consultation_revenue", 0.0)
    t_rev = report.get("test_revenue", 0.0)
    ins_cov = report.get("insurance_coverage", 0.0)
    sen_disc = report.get("senior_discounts", 0.0)
    p_rev = report.get("patient_revenue", 0.0)

    spec = report.get("most_requested_specialization", "N/A")
    h_pat = report.get("highest_spending_patient", "N/A")
    no_bill_cnt = report.get("completed_without_bill_count", 0)

    print("========================================")
    print("           CLINIC DASHBOARD             ")
    print("========================================")
    print(f"Total Patients: {tot_p}")
    print(f"Total Doctors: {tot_d}")
    print(f"Total Appointments: {tot_a}")
    print(f"Completed: {comp}")
    print(f"Cancelled: {canc}")
    print(f"Pending: {pend}")
    print(f"Total Consultation Revenue: ${c_rev:,.2f}")
    print(f"Total Test Revenue: ${t_rev:,.2f}")
    print(f"Total Insurance Coverage: ${ins_cov:,.2f}")
    print(f"Total Senior Discounts: ${sen_disc:,.2f}")
    print(f"Total Patient Revenue: ${p_rev:,.2f}")
    print(f"Most Requested Specialization: {spec}")
    print(f"Highest Spending Patient: {h_pat}")
    print("========================================")

    if no_bill_cnt > 0:
        print(f"Warning: {no_bill_cnt} completed appointment has no bill.")