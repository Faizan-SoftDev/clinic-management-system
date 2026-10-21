# Clinic Management System

## 1. Overview
A zero-dependency, high-performance command-line clinic management dashboard built to demonstrate Python core principles. The application structures data models around human profiles, automated dynamic billing calculators, cross-validated appointment constraints, and stable analytical reports. 

All runtime state structures live locally in Python `dictionaries` and `lists`. The project contains zero external database engines, web frameworks, or third-party package dependencies.

---

## 2. Features and Core System Capabilities
- **Full CRUD Validations:** Robust administrative management over patients, doctors, scheduled logs, and master item cost files.
- **Collision Blocker Engine:** Real-time prevention of duplicate appointment submissions or double-booking time slots for identical doctors.
- **Deterministic Tie-Breakers:** High-fidelity reporting metrics that fallback safely to original configuration insertion tracking indices when analytics values match.
- **Functional Modularity:** Clean boundary patterns separating data presentation schemas from operational calculation codeblocks.

---

## 3. Financial Computations & Billing Rules
The invoice processor compiles totals dynamically using the following hierarchical calculation roadmap:
1. **Subtotal Base Calculation:** Unpacks custom arrays using `*args` to compute `Consultation Fee` + `Sum of Unique Medical Tests`.
2. **Insurance Deductions:** If active, insurance coverage deducts **20%** off consultation fees and **50%** off valid test charges.
3. **Senior Citizen Relief:** Patients aged **60 or older** receive an extra **10% discount** calculated against the remaining post-insurance balance.
4. **Historical Price Stability:** Completed visit records permanently embed calculation states inside isolated snapshots at boot execution times. Later configuration rate updates do not retroactively skew past financial records.

### Case Invariance Constraints
- Medical target keys are sanitized via structural `casefold()` / `.lower()` pipelines to enforce safe keyword pricing matching. Duplicate inputs on similar diagnostic items return clean validation failure states.

---

## 4. Advanced Architecture & Scope Closure Design
- **Tuple Routing Interface:** Internal business operations strictly communicate using predictable outcome signatures like `(True, Success_Data)` or `(False, Error_Reason_String)`.
- **Python Functional Closures:** The senior citizen calculation engine is built using nested **Functional Closures**. It traps config boundaries inside an inner runtime reference stack, illustrating pure **LEGB (Local, Enclosing, Global, Built-in)** scoping lookup layers. It processes logic pools without mutating global application dictionaries.

---

## 5. Quick Start and Installation
The system requires a standard installation of **Python 3.8+**.

### Booting the Interactive CLI Portal
To launch the system interface control panel, execute the following script from your root project directory terminal:
```bash
python3 app.py