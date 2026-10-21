"""Billing calculations for the Clinic Management System."""

from config import CLINIC_CONFIG, create_senior_discount_calculator
from validation import is_non_negative_number, validate_tests


def calculate_total(*charges):
    """Sum non-negative numeric charges using *args, or return a failure reason."""
    total = 0

    for charge in charges:
        if not is_non_negative_number(charge):
            return False, "Every charge must be a non-negative number."

        total += charge

    return True, total


def calculate_test_charges(tests, test_prices):
    """Calculate medical test charges after validating the test list."""
    if not isinstance(test_prices, dict):
        return False, "Test prices must be provided as a dictionary."

    validation_result = validate_tests(tests, test_prices)

    if not validation_result[0]:
        return False, validation_result[1]

    prices = {
        name.casefold(): price
        for name, price in test_prices.items()
        if isinstance(name, str)
    }
    return True, sum(prices[test.casefold()] for test in tests)


def calculate_insurance_coverage(
    consultation_fee,
    test_charges,
    insurance,
    config=None,
):
    """Calculate the insurance contribution before senior discount."""
    if config is None:
        config = CLINIC_CONFIG

    for name, amount in (
        ("Consultation fee", consultation_fee),
        ("Test charges", test_charges),
    ):
        if not is_non_negative_number(amount):
            return False, f"{name} must be a non-negative number."

    if not isinstance(insurance, bool):
        return False, "Insurance must be True or False."

    if not isinstance(config, dict):
        return False, "Clinic configuration must be a dictionary."

    consultation_rate = config.get("consultation_insurance_rate")
    test_rate = config.get("test_insurance_rate")

    for name, rate in (
        ("Consultation insurance rate", consultation_rate),
        ("Test insurance rate", test_rate),
    ):
        if not is_non_negative_number(rate) or rate > 1:
            return False, f"{name} must be between 0 and 1."

    if not insurance:
        return True, {
            "consultation_coverage": 0,
            "test_coverage": 0,
            "total_coverage": 0,
        }

    consultation_coverage = consultation_fee * consultation_rate
    test_coverage = test_charges * test_rate

    return True, {
        "consultation_coverage": consultation_coverage,
        "test_coverage": test_coverage,
        "total_coverage": consultation_coverage + test_coverage,
    }


def calculate_bill(
    consultation_fee,
    tests=None,
    test_prices=None,
    age=0,
    **options,
):
    """Calculate the final patient bill using **kwargs for configuration toggles."""
    allowed_options = {
        "insurance",
        "senior_discount",
        "include_tests",
        "config",
    }

    unknown_options = set(options) - allowed_options

    if unknown_options:
        return False, (
            f"Unknown billing option(s): {', '.join(sorted(unknown_options))}."
        )

    if not is_non_negative_number(consultation_fee):
        return False, "Consultation fee must be a non-negative number."

    if isinstance(age, bool) or not isinstance(age, int) or age < 0:
        return False, "Age must be a non-negative integer."

    insurance = options.get("insurance", False)
    senior_discount = options.get("senior_discount", True)
    include_tests = options.get("include_tests", True)
    config = options.get("config", CLINIC_CONFIG)

    if tests is None:
        tests = []

    if test_prices is None:
        test_prices = {}

    if include_tests:
        test_result = calculate_test_charges(tests, test_prices)

        if not test_result[0]:
            return False, test_result[1]

        test_charges = test_result[1]
    else:
        test_charges = 0

    subtotal_result = calculate_total(consultation_fee, test_charges)

    if not subtotal_result[0]:
        return False, subtotal_result[1]

    subtotal = subtotal_result[1]

    insurance_result = calculate_insurance_coverage(
        consultation_fee,
        test_charges,
        insurance,
        config,
    )

    if not insurance_result[0]:
        return False, insurance_result[1]

    coverage = insurance_result[1]
    amount_after_insurance = subtotal - coverage["total_coverage"]

    discount_calculator = create_senior_discount_calculator(config)

    if senior_discount:
        discount_amount = discount_calculator(amount_after_insurance, age)
    else:
        discount_amount = 0

    final_amount = amount_after_insurance - discount_amount

    return True, {
        "consultation_fee": consultation_fee,
        "test_charges": test_charges,
        "subtotal": subtotal,
        "consultation_coverage": coverage["consultation_coverage"],
        "test_coverage": coverage["test_coverage"],
        "insurance_coverage": coverage["total_coverage"],
        "amount_after_insurance": amount_after_insurance,
        "senior_discount": discount_amount,
        "final_bill": final_amount,
        "currency": config.get("currency", "$"),
    }