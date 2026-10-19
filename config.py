"""Central configuration for the clinic."""

CLINIC_CONFIG = {
    "currency": "$",
    "consultation_insurance_rate": 0.20,
    "test_insurance_rate": 0.50,
    "senior_age": 60,
    "senior_discount_rate": 0.10,
}


def create_senior_discount_calculator(config):
    """Build a calculator that closes over the clinic's discount settings."""
    senior_age = config["senior_age"]
    discount_rate = config["senior_discount_rate"]

    def calculate_discount(amount, age):
        if age >= senior_age:
            return amount * discount_rate
        return 0

    return calculate_discount
