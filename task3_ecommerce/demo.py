from ecommerce import DatabaseConfigManager, PaymentFactory, Order, OrderService, LogisticsListener, InvoiceListener, EmailListener

config = DatabaseConfigManager()
print("Environment:", config.get("environment"))
order = Order("ORD-1001")
for listener in (LogisticsListener(), InvoiceListener(), EmailListener()):
    order.subscribe(listener)
print(OrderService(PaymentFactory()).pay_order(order, "paypal", "49.99", "USD"))
print("Order status:", order.status)
order.set_status("shipped")
