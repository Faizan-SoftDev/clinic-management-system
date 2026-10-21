"""Central configuration for the Clinic Management System."""

CLINIC_CONFIG = {
    "currency": "$",
    "consultation_insurance_rate": 0.20,
    "test_insurance_rate": 0.50,
    "senior_age": 60,
    "senior_discount_rate": 0.10,
}


def validate_clinic_config(config):
    """Validate the clinic configuration."""
    if not isinstance(config, dict):
        return False, "Configuration must be a dictionary."

    required_keys = (
        "currency",
        "consultation_insurance_rate",
        "test_insurance_rate",
        "senior_age",
        "senior_discount_rate",
    )

    for key in required_keys:
        if key not in config:
            return False, f"Missing configuration setting: {key}"

    if not isinstance(config["currency"], str) or not config["currency"].strip():
        return False, "Currency must be a non-empty string."

    for key in (
        "consultation_insurance_rate",
        "test_insurance_rate",
        "senior_discount_rate",
    ):
        value = config[key]

        if (
            not isinstance(value, (int, float))
            or isinstance(value, bool)
            or not 0 <= value <= 1
        ):
            return False, f"{key} must be a number between 0 and 1."

    senior_age = config["senior_age"]

    if (
        not isinstance(senior_age, int)
        or isinstance(senior_age, bool)
        or senior_age < 0
    ):
        return False, "Senior age must be a non-negative integer."

    return True, "Configuration is valid."


def create_senior_discount_calculator(config):
    """Create a discount calculator using the supplied configuration."""
    valid, message = validate_clinic_config(config)

    if not valid:
        raise ValueError(message)

    senior_age = config["senior_age"]
    discount_rate = config["senior_discount_rate"]

    def calculate_discount(amount, age):
        if (
            not isinstance(amount, (int, float))
            or isinstance(amount, bool)
            or amount < 0
        ):
            raise ValueError("Amount must be a non-negative number.")

        if (
            not isinstance(age, int)
            or isinstance(age, bool)
            or age < 0
        ):
            raise ValueError("Age must be a non-negative integer.")

        if age >= senior_age:
            return amount * discount_rate

        return 0.0

    return calculate_discount