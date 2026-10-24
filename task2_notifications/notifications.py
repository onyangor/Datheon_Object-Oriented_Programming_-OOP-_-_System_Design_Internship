"""Task 2: extensible notification framework using SOLID principles."""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Iterable


@dataclass(frozen=True)
class Notification:
    recipient: str
    message: str
    subject: str = ""

    def __post_init__(self):
        if not self.recipient.strip(): raise ValueError("Recipient is required")
        if not self.message.strip(): raise ValueError("Message is required")


@dataclass(frozen=True)
class SendResult:
    channel: str
    recipient: str
    success: bool
    detail: str


class NotificationChannel(ABC):
    """Small interface: every channel only needs to implement send()."""
    @property
    @abstractmethod
    def name(self) -> str: ...

    @abstractmethod
    def send(self, notification: Notification) -> SendResult: ...


class EmailSender(NotificationChannel):
    @property
    def name(self): return "email"
    def send(self, notification):
        # Replace this simulation with an SMTP/API adapter in a real deployment.
        return SendResult(self.name, notification.recipient, True, "Email accepted by demo adapter")


class SMSSender(NotificationChannel):
    @property
    def name(self): return "sms"
    def send(self, notification):
        return SendResult(self.name, notification.recipient, True, "SMS accepted by demo adapter")


class SlackSender(NotificationChannel):
    @property
    def name(self): return "slack"
    def send(self, notification):
        return SendResult(self.name, notification.recipient, True, "Slack message accepted by demo adapter")


class WhatsAppSender(NotificationChannel):
    @property
    def name(self): return "whatsapp"
    def send(self, notification):
        return SendResult(self.name, notification.recipient, True, "WhatsApp message accepted by demo adapter")


class NotificationService:
    """Orchestrates delivery; channel implementations are injected from outside."""
    def __init__(self, channels: Iterable[NotificationChannel]):
        self._channels = tuple(channels)
        if not self._channels: raise ValueError("At least one channel is required")
        names = [channel.name for channel in self._channels]
        if len(set(names)) != len(names): raise ValueError("Channel names must be unique")

    def notify(self, notification: Notification) -> list[SendResult]:
        results = []
        for channel in self._channels:
            try:
                results.append(channel.send(notification))
            except Exception as exc:
                # Isolate one provider's failure so other channels still run.
                results.append(SendResult(channel.name, notification.recipient, False, str(exc)))
        return results
