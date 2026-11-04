"""In-memory dataset with automatic historical bill seeding on initialization."""

from typing import Dict, List, Any
from config import CLINIC_CONFIG

patients: Dict[str, Any] = {
    "P001": {"name": "Ali Khan", "age": 32, "city": "Lahore", "insurance": True},
    "P002": {"name": "Ahmed Raza", "age": 45, "city": "Multan", "insurance": False},
    "P003": {"name": "Sara Ahmed", "age": 28, "city": "Lahore", "insurance": True},
    "P004": {"name": "Usman Ali", "age": 67, "city": "Islamabad", "insurance": False},
}

doctors: Dict[str, Any] = {
    "D001": {"name": "Dr. Hassan", "specialization": "Cardiology", "fee": 5000, "available": True},
    "D002": {"name": "Dr. Sara", "specialization": "Dermatology", "fee": 3000, "available": True},
    "D003": {"name": "Dr. Ahmed", "specialization": "General", "fee": 2000, "available": True},
}

test_prices: Dict[str, float] = {
    "ECG": 1500,
    "Blood Test": 1000,
    "X-Ray": 2500,
    "MRI": 8000,
}

appointments: List[Dict[str, Any]] = [
    {
        "appointment_id": "A001",
        "patient_id": "P001",
        "doctor_id": "D001",
        "status": "completed",
        "tests": ["ECG", "Blood Test"],
        "date": "2026-11-01",
        "time_slot": "09:00 AM",
        "processed": True,
        # Frozen historical bill record (must not be overwritten)
        "bill": {
            "consultation_fee": 5000.0,
            "tests": ["ECG", "Blood Test"],
            "test_charges": 2500.0,
            "subtotal": 7500.0,
            "insurance_applied": True,
            "consultation_coverage": 1000.0,
            "test_coverage": 1250.0,
            "insurance_coverage": 2250.0,
            "net_after_insurance": 5250.0,
            "senior_discount": 0.0,
            "final_bill": 4200.0,
        },
    },
    {
        "appointment_id": "A002",
        "patient_id": "P002",
        "doctor_id": "D003",
        "status": "completed",
        "tests": [],
        "date": "2026-11-01",
        "time_slot": "10:00 AM",
    },
    {
        "appointment_id": "A003",
        "patient_id": "P003",
        "doctor_id": "D002",
        "status": "cancelled",
        "tests": [],
        "date": "2026-11-01",
        "time_slot": "11:00 AM",
    },
    {
        "appointment_id": "A004",
        "patient_id": "P004",
        "doctor_id": "D001",
        "status": "completed",
        "tests": ["ECG"],
        "date": "2026-11-02",
        "time_slot": "09:00 AM",
    },
]


def seed_completed_appointments(
    apps: List[Dict[str, Any]],
    pats: Dict[str, Any],
    docs: Dict[str, Any],
    prices: Dict[str, float],
    config: Dict[str, Any],
) -> None:
    """Seed bills only for completed appointments that do not have an existing bill."""
    from billing import calculate_bill

    for app in apps:
        if not isinstance(app, dict) or app.get("status") != "completed":
            continue
        # Preserve pre-existing historical bills
        if "bill" in app and isinstance(app["bill"], dict) and app["bill"]:
            continue

        pid = app.get("patient_id")
        did = app.get("doctor_id")

        if pid in pats and did in docs:
            patient = pats[pid]
            doctor = docs[did]

            res = calculate_bill(
                doctor["fee"],
                app.get("tests", []),
                prices,
                patient.get("age", 0),
                insurance=patient.get("insurance", False),
                senior_discount=True,
                include_tests=True,
                config=config,
            )
            if isinstance(res, tuple) and res[0]:
                app["bill"] = res[1]
                app["processed"] = True


seed_completed_appointments(appointments, patients, doctors, test_prices, CLINIC_CONFIG)