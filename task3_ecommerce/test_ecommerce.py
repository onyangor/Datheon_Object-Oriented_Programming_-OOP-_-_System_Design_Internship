import unittest
from decimal import Decimal
from .ecommerce import (DatabaseConfigManager, PaymentFactory, PaymentHandler, Payment, Order,
                       OrderObserver, OrderService, CreditCardHandler)

class Recorder(OrderObserver):
    def __init__(self): self.events = []
    def update(self, order_id, status): self.events.append((order_id, status))

class CustomHandler(PaymentHandler):
    def pay(self, payment): return "custom"

class EcommerceTests(unittest.TestCase):
    def test_singleton(self):
        self.assertIs(DatabaseConfigManager(), DatabaseConfigManager())

    def test_factory_creates_handlers(self):
        self.assertIsInstance(PaymentFactory().create("credit_card"), CreditCardHandler)

    def test_factory_extensible(self):
        factory = PaymentFactory()
        factory.register("custom", CustomHandler)
        self.assertEqual(factory.create("custom").pay(Payment(Decimal("1"))), "custom")

    def test_observers_receive_status(self):
        order = Order("o1"); observer = Recorder(); order.subscribe(observer)
        order.set_status("paid")
        self.assertEqual(observer.events, [("o1", "paid")])

    def test_unsubscribe(self):
        order = Order("o1"); observer = Recorder()
        order.subscribe(observer); order.unsubscribe(observer); order.set_status("shipped")
        self.assertEqual(observer.events, [])

    def test_order_service_payment(self):
        order = Order("o1")
        message = OrderService(PaymentFactory()).pay_order(order, "paypal", "10.00")
        self.assertIn("PayPal", message)
        self.assertEqual(order.status, "paid")

    def test_invalid_payment_amount(self):
        with self.assertRaises(ValueError): OrderService(PaymentFactory()).pay_order(Order("o"), "paypal", "-1")

if __name__ == "__main__": unittest.main()
