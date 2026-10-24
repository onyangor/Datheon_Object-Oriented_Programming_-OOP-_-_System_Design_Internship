# OOP & System Design Internship — Batch 01

**Student:** Ray Beckham Onyango Otieno  
**Email:** onyangoraybeckham@gmail.com  
**Application ID:** DT-2026-XJS59  
**Program:** Object-Oriented Programming (OOP) & System Design Internship  
**Language:** Python 3.10+  
**Status:** Project work in progress

## Overview

This repository contains four independently runnable projects built to practise object-oriented programming, SOLID principles, design patterns, and low-level system design. The implementations use Python's standard library and include unit tests and demonstration scripts.

## Projects

### Task 1 — Multi-Currency Banking & Ledger Engine
Demonstrates the four pillars of OOP:
- **Encapsulation:** account state is protected behind methods and properties.
- **Inheritance:** savings, checking, and high-yield accounts extend the account base class.
- **Abstraction:** the abstract `Account` class defines interest and fee operations.
- **Polymorphism:** a shared transaction processor works with different account types.

Also includes `Decimal` monetary values, basic input validation, same-currency transfers, and an in-memory ledger.

### Task 2 — Notification & Alert Dispatch Framework
Demonstrates SOLID-oriented design with an abstract notification-channel interface, separate channel classes, and dependency injection into `NotificationService`. Includes Email, SMS, Slack, and WhatsApp demo adapters, as well as failure isolation when a channel raises an exception.

**Note:** The channel classes simulate delivery; they do not send real messages.

### Task 3 — E-Commerce Order Pipeline
Demonstrates a Singleton configuration manager, a payment factory, and Observer notifications for order status changes. Includes handlers for Credit Card, UPI, PayPal, and Crypto.

**Note:** Payment handlers simulate responses and do not connect to real payment providers. The configuration manager is in-memory and is not a production database.

### Task 4 — Smart Parking Lot
Demonstrates an object-oriented low-level design for a multi-floor parking lot. Includes vehicle and slot types, compatibility checks, first-fit slot allocation, ticket generation, hourly pricing, and checkout receipts. A Mermaid UML class diagram is provided in `task4_parking/uml.md`.

## Repository Structure

```text
oop_system_design_projects/
├── README.md
├── task1_banking/
│   ├── banking.py
│   ├── demo.py
│   └── test_banking.py
├── task2_notifications/
│   ├── notifications.py
│   ├── demo.py
│   └── test_notifications.py
├── task3_ecommerce/
│   ├── ecommerce.py
│   ├── demo.py
│   └── test_ecommerce.py
└── task4_parking/
    ├── parking.py
    ├── demo.py
    ├── test_parking.py
    └── uml.md
```

## Requirements

- Python 3.10 or later
- No third-party Python packages required

Check your Python version:

```bash
python --version
```

## How to Run

Open a terminal in the repository root and run a demo:

```bash
python task1_banking/demo.py
python task2_notifications/demo.py
python task3_ecommerce/demo.py
python task4_parking/demo.py
```

Run all unit tests from the repository root:

```bash
python -m unittest discover -s . -p "test_*.py" -v
```

Alternatively, run a specific test file from its task directory, for example:

```bash
cd task1_banking
python -m unittest -v test_banking.py
```

## Testing

The tests cover invalid deposits and withdrawals, account transfers and currency mismatch, interest and fee processing, adding a notification channel, handling a provider failure, Singleton identity, registering a payment handler, Observer notifications, parking-slot compatibility, hourly pricing, duplicate active vehicles, and ticket closure.

## Design Notes and Limitations

This is an educational project demonstrating design concepts, not a production banking, messaging, payment, or parking service.

- The ledger and configuration are in-memory; data does not persist after the program exits.
- Cross-currency transfers are rejected until an explicit foreign-exchange service is implemented.
- Notification and payment providers are simulated.
- A production system would require persistent storage, authentication and authorization, secure secret management, audit logging, stronger transaction/concurrency guarantees, monitoring, and provider-specific error handling.
- Parking prices and slot compatibility are illustrative rules and can be adjusted to match specific requirements.

## Learning Outcomes

Through these projects, I am practising:
1. Designing classes with clear responsibilities and controlled state.
2. Applying abstract base classes, inheritance, and polymorphism.
3. Decoupling services from concrete implementations.
4. Using common design patterns to structure an application.
5. Writing unit tests for expected behavior and invalid input.
6. Documenting system structure and explaining design decisions.

## Author

**Ray Beckham Onyango Otieno**  
Computer Science Graduate | Python OOP & System Design Projects
