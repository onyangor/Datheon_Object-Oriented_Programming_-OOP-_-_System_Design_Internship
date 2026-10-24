from notifications import Notification, NotificationService, EmailSender, SMSSender, SlackSender, WhatsAppSender

service = NotificationService([EmailSender(), SMSSender(), SlackSender(), WhatsAppSender()])
for result in service.notify(Notification("customer-123", "Your order has shipped", "Order update")):
    print(result)
