"""Central configuration for the clinic."""
from typing import Dict, Any, Callable

# 1. Global Scope (G): Shared across the entire module
CLINIC_CONFIG: Dict[str, Any] = {
    "currency": "$",
    "consultation_insurance_rate": 0.20,
    "test_insurance_rate": 0.50,
    "senior_age": 60,
    "senior_discount_rate": 0.10,
}


def create_senior_discount_calculator(config: Dict[str, Any]) -> Callable[[float, int], float]:
    """Build a calculator that closes over the clinic's discount settings.

    This fulfills the LEGB requirement using an enclosing scope closure.
    """
    # 2. Enclosing Scope (E): Variables captured by the inner closure function
    # Using .get() prevents KeyError crashes if keys are accidentally removed
    senior_age = config.get("senior_age", 60)
    discount_rate = config.get("senior_discount_rate", 0.10)

    def calculate_discount(amount: float, age: int) -> float:
        # 3. Local Scope (L): Function parameters (amount, age)
        # 4. Built-in Scope (B): Using Python's built-in float/int types
        if age >= senior_age:
            return amount * discount_rate
        return 0.0

    return calculate_discount
