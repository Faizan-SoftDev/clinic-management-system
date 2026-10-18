"""In-memory data for the Clinic Management System."""

patients = {
    "P001": {
        "name": "Ali Khan",
        "age": 32,
        "city": "Lahore",
        "insurance": True,
    },
    "P002": {
        "name": "Ahmed Raza",
        "age": 45,
        "city": "Multan",
        "insurance": False,
    },
    "P003": {
        "name": "Sara Ahmed",
        "age": 28,
        "city": "Lahore",
        "insurance": True,
    },
    "P004": {
        "name": "Usman Ali",
        "age": 67,
        "city": "Islamabad",
        "insurance": False,
    },
}

doctors = {
    "D001": {
        "name": "Dr. Hassan",
        "specialization": "Cardiology",
        "fee": 5000,
        "available": True,
    },
    "D002": {
        "name": "Dr. Sara",
        "specialization": "Dermatology",
        "fee": 3000,
        "available": True,
    },
    "D003": {
        "name": "Dr. Ahmed",
        "specialization": "General",
        "fee": 2000,
        "available": True,
    },
}

appointments = [
    {
        "appointment_id": "A001",
        "patient_id": "P001",
        "doctor_id": "D001",
        "status": "completed",
        "tests": ["ECG", "Blood Test"],
    },
    {
        "appointment_id": "A002",
        "patient_id": "P002",
        "doctor_id": "D003",
        "status": "completed",
        "tests": [],
    },
    {
        "appointment_id": "A003",
        "patient_id": "P003",
        "doctor_id": "D002",
        "status": "cancelled",
        "tests": [],
    },
    {
        "appointment_id": "A004",
        "patient_id": "P004",
        "doctor_id": "D001",
        "status": "completed",
        "tests": ["ECG"],
    },
]

test_prices = {
    "ECG": 1500,
    "Blood Test": 1000,
    "X-Ray": 2500,
    "MRI": 8000,
}
