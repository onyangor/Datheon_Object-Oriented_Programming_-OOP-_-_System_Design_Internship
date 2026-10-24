import unittest
from .notifications import Notification, NotificationChannel, NotificationService, SendResult, EmailSender, SMSSender

class BrokenSender(NotificationChannel):
    @property
    def name(self): return "broken"
    def send(self, notification): raise RuntimeError("provider unavailable")

class FakeSender(NotificationChannel):
    @property
    def name(self): return "fake"
    def send(self, notification): return SendResult(self.name, notification.recipient, True, "sent")

class NotificationTests(unittest.TestCase):
    def test_all_injected_channels_receive_notification(self):
        service = NotificationService([EmailSender(), SMSSender()])
        results = service.notify(Notification("person@example.com", "Hello"))
        self.assertEqual([r.channel for r in results], ["email", "sms"])
        self.assertTrue(all(r.success for r in results))

    def test_new_channel_plugs_in_without_service_changes(self):
        result = NotificationService([FakeSender()]).notify(Notification("x", "Hi"))
        self.assertEqual(result[0].channel, "fake")

    def test_one_provider_failure_does_not_stop_others(self):
        results = NotificationService([BrokenSender(), FakeSender()]).notify(Notification("x", "Hi"))
        self.assertFalse(results[0].success)
        self.assertTrue(results[1].success)

    def test_empty_notification_rejected(self):
        with self.assertRaises(ValueError): Notification("", "hello")

    def test_duplicate_channel_names_rejected(self):
        with self.assertRaises(ValueError): NotificationService([EmailSender(), EmailSender()])

if __name__ == "__main__": unittest.main()
