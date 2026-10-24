"""Task 3: Singleton, Factory Method-style payment factory, Observer order events."""
from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from threading import RLock
from typing import Callable


class DatabaseConfigManager:
    """Thread-safe process-local Singleton. Not a substitute for a real database."""
    _instance = None
    _instance_lock = RLock()

    def __new__(cls):
        with cls._instance_lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._initialized = False
            return cls._instance

    def __init__(self):
        if self._initialized: return
        self._values = {"environment": "development", "database_url": "sqlite:///orders.db"}
        self._lock = RLock()
        self._initialized = True

    def get(self, key, default=None):
        with self._lock: return self._values.get(key, default)

    def set(self, key, value):
        if not key: raise ValueError("Config key cannot be empty")
        with self._lock: self._values[key] = value


@dataclass(frozen=True)
class Payment:
    amount: Decimal
    currency: str = "USD"


class PaymentHandler(ABC):
    @abstractmethod
    def pay(self, payment: Payment) -> str: ...


class CreditCardHandler(PaymentHandler):
    def pay(self, payment): return f"Credit card payment authorized: {payment.amount} {payment.currency}"


class UPIHandler(PaymentHandler):
    def pay(self, payment): return f"UPI payment initiated: {payment.amount} {payment.currency}"


class PayPalHandler(PaymentHandler):
    def pay(self, payment): return f"PayPal payment initiated: {payment.amount} {payment.currency}"


class CryptoHandler(PaymentHandler):
    def pay(self, payment): return f"Crypto payment initiated: {payment.amount} {payment.currency}"


class PaymentFactory:
    """Maps a payment choice to a handler; add new handlers here or register at runtime."""
    def __init__(self):
        self._handlers = {
            "credit_card": CreditCardHandler,
            "upi": UPIHandler,
            "paypal": PayPalHandler,
            "crypto": CryptoHandler,
        }

    def register(self, name: str, handler_type):
        if not name.strip(): raise ValueError("Payment name cannot be empty")
        if not isinstance(handler_type, type) or not issubclass(handler_type, PaymentHandler):
            raise TypeError("Handler must be a PaymentHandler subclass")
        self._handlers[name.lower()] = handler_type

    def create(self, name: str) -> PaymentHandler:
        try: return self._handlers[name.lower()]()
        except KeyError as exc: raise ValueError(f"Unsupported payment method: {name}") from exc


class OrderObserver(ABC):
    @abstractmethod
    def update(self, order_id: str, status: str) -> None: ...


class LogisticsListener(OrderObserver):
    def update(self, order_id, status): print(f"[logistics] {order_id}: {status}")


class InvoiceListener(OrderObserver):
    def update(self, order_id, status): print(f"[invoicing] {order_id}: {status}")


class EmailListener(OrderObserver):
    def update(self, order_id, status): print(f"[email] {order_id}: {status}")


class Order:
    ALLOWED_STATUSES = {"created", "paid", "packed", "shipped", "delivered", "cancelled"}

    def __init__(self, order_id: str):
        if not order_id.strip(): raise ValueError("order_id is required")
        self.order_id = order_id
        self._status = "created"
        self._observers: list[OrderObserver] = []
        self._lock = RLock()

    @property
    def status(self): return self._status

    def subscribe(self, observer: OrderObserver):
        with self._lock:
            if observer not in self._observers: self._observers.append(observer)

    def unsubscribe(self, observer: OrderObserver):
        with self._lock:
            if observer in self._observers: self._observers.remove(observer)

    def set_status(self, status: str):
        status = status.lower()
        if status not in self.ALLOWED_STATUSES: raise ValueError("Unknown order status")
        with self._lock:
            if status == self._status: return
            self._status = status
            observers = tuple(self._observers)
        # Notify outside the lock so observers can safely call back into the order.
        errors = []
        for observer in observers:
            try: observer.update(self.order_id, status)
            except Exception as exc: errors.append(exc)
        if errors:
            # Status remains changed; caller can log/report observer errors.
            raise RuntimeError(f"{len(errors)} observer(s) failed") from errors[0]


class OrderService:
    def __init__(self, payment_factory: PaymentFactory):
        self._payment_factory = payment_factory

    def pay_order(self, order: Order, method: str, amount, currency="USD"):
        try: value = Decimal(str(amount))
        except (InvalidOperation, ValueError) as exc: raise ValueError("Invalid amount") from exc
        if not value.is_finite() or value <= 0: raise ValueError("Amount must be positive and finite")
        result = self._payment_factory.create(method).pay(Payment(value, currency.upper()))
        order.set_status("paid")
        return result
