"""Task 4: smart parking lot LLD with compatibility and pluggable pricing."""
from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal, ROUND_CEILING
from enum import Enum
from threading import RLock
from uuid import uuid4


class VehicleType(str, Enum):
    MOTORCYCLE = "motorcycle"
    COMPACT = "compact"
    SUV = "large_suv"
    ELECTRIC = "electric"


@dataclass(frozen=True)
class Vehicle:
    plate: str
    vehicle_type: VehicleType
    electric: bool = False

    def __post_init__(self):
        if not self.plate.strip(): raise ValueError("Vehicle plate is required")
        if self.vehicle_type == VehicleType.ELECTRIC and not self.electric:
            object.__setattr__(self, "electric", True)


class SlotType(str, Enum):
    MOTORCYCLE = "motorcycle"
    COMPACT = "compact"
    LARGE = "large"
    EV_CHARGING = "ev_charging"


@dataclass(frozen=True)
class ParkingTicket:
    ticket_id: str
    vehicle_plate: str
    floor_number: int
    slot_id: str
    entry_time: datetime


@dataclass(frozen=True)
class ParkingReceipt:
    ticket: ParkingTicket
    exit_time: datetime
    duration_hours: int
    amount: Decimal


class PricingStrategy(ABC):
    @abstractmethod
    def calculate(self, vehicle: Vehicle, hours: int) -> Decimal: ...


class HourlyPricing(PricingStrategy):
    def __init__(self, rates=None):
        self._rates = rates or {
            VehicleType.MOTORCYCLE: Decimal("50.00"),
            VehicleType.COMPACT: Decimal("100.00"),
            VehicleType.SUV: Decimal("200.00"),
            VehicleType.ELECTRIC: Decimal("150.00"),
        }

    def calculate(self, vehicle, hours):
        if hours < 1: raise ValueError("Hours must be at least one")
        rate = self._rates[vehicle.vehicle_type]
        return (rate * hours).quantize(Decimal("0.01"))


class ParkingSlot:
    def __init__(self, slot_id: str, slot_type: SlotType):
        if not slot_id.strip(): raise ValueError("slot_id is required")
        self.slot_id = slot_id
        self.slot_type = slot_type
        self._ticket_id = None
        self._lock = RLock()

    @property
    def occupied(self):
        with self._lock: return self._ticket_id is not None

    def can_fit(self, vehicle: Vehicle):
        if self.slot_type == SlotType.EV_CHARGING:
            return vehicle.electric
        if vehicle.vehicle_type == VehicleType.MOTORCYCLE:
            return self.slot_type in (SlotType.MOTORCYCLE, SlotType.COMPACT, SlotType.LARGE)
        if vehicle.vehicle_type == VehicleType.COMPACT:
            return self.slot_type in (SlotType.COMPACT, SlotType.LARGE)
        if vehicle.vehicle_type == VehicleType.SUV:
            return self.slot_type == SlotType.LARGE
        if vehicle.vehicle_type == VehicleType.ELECTRIC:
            # EVs may use standard slots if no charging is required; this model treats EVs as electric.
            return self.slot_type in (SlotType.EV_CHARGING, SlotType.COMPACT, SlotType.LARGE)
        return False

    def reserve(self, ticket_id: str, vehicle: Vehicle):
        with self._lock:
            if self._ticket_id is not None or not self.can_fit(vehicle): return False
            self._ticket_id = ticket_id
            return True

    def release(self, ticket_id: str):
        with self._lock:
            if self._ticket_id != ticket_id: return False
            self._ticket_id = None
            return True


class ParkingFloor:
    def __init__(self, floor_number: int, slots: list[ParkingSlot]):
        self.floor_number = floor_number
        self._slots = list(slots)

    @property
    def slots(self): return tuple(self._slots)


class ParkingLot:
    def __init__(self, floors: list[ParkingFloor], pricing: PricingStrategy | None = None):
        if not floors: raise ValueError("Parking lot needs at least one floor")
        self._floors = list(floors)
        self._pricing = pricing or HourlyPricing()
        self._active: dict[str, tuple[ParkingTicket, ParkingSlot, Vehicle]] = {}
        self._closed: set[str] = set()
        self._lock = RLock()

    @property
    def floors(self): return tuple(self._floors)

    def park(self, vehicle: Vehicle, entry_time: datetime | None = None) -> ParkingTicket:
        entry_time = entry_time or datetime.now(timezone.utc)
        if entry_time.tzinfo is None: raise ValueError("entry_time must be timezone-aware")
        with self._lock:
            if any(ticket.vehicle_plate == vehicle.plate for ticket, _, _ in self._active.values()):
                raise ValueError("This vehicle already has an active ticket")
            # First-fit allocation: first compatible free slot by floor then slot order.
            for floor in self._floors:
                for slot in floor.slots:
                    ticket_id = str(uuid4())
                    if slot.reserve(ticket_id, vehicle):
                        ticket = ParkingTicket(ticket_id, vehicle.plate, floor.floor_number, slot.slot_id, entry_time)
                        self._active[ticket_id] = (ticket, slot, vehicle)
                        return ticket
            raise RuntimeError("No compatible parking slot available")

    def leave(self, ticket_id: str, exit_time: datetime | None = None) -> ParkingReceipt:
        exit_time = exit_time or datetime.now(timezone.utc)
        if exit_time.tzinfo is None: raise ValueError("exit_time must be timezone-aware")
        with self._lock:
            if ticket_id in self._closed: raise ValueError("Ticket has already been closed")
            if ticket_id not in self._active: raise ValueError("Unknown active ticket")
            ticket, slot, vehicle = self._active[ticket_id]
            if exit_time < ticket.entry_time: raise ValueError("Exit time cannot precede entry time")
            seconds = (exit_time - ticket.entry_time).total_seconds()
            hours = max(1, int((Decimal(str(seconds)) / Decimal("3600")).to_integral_value(rounding=ROUND_CEILING)))
            amount = self._pricing.calculate(vehicle, hours)
            if not slot.release(ticket_id): raise RuntimeError("Slot state mismatch")
            del self._active[ticket_id]
            self._closed.add(ticket_id)
            return ParkingReceipt(ticket, exit_time, hours, amount)
