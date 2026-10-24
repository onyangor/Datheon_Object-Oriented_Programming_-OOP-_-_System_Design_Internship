import unittest
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from .parking import (ParkingFloor, ParkingLot, ParkingSlot, SlotType, Vehicle, VehicleType, HourlyPricing)

def make_lot():
    floor1 = ParkingFloor(1, [
        ParkingSlot("M1", SlotType.MOTORCYCLE),
        ParkingSlot("C1", SlotType.COMPACT),
        ParkingSlot("L1", SlotType.LARGE),
        ParkingSlot("E1", SlotType.EV_CHARGING),
    ])
    return ParkingLot([floor1])

class ParkingTests(unittest.TestCase):
    def test_compatible_allocation(self):
        lot = make_lot()
        ticket = lot.park(Vehicle("KAA1", VehicleType.SUV))
        self.assertEqual(ticket.slot_id, "L1")

    def test_full_compatible_slot_types(self):
        lot = ParkingLot([ParkingFloor(1, [ParkingSlot("M1", SlotType.MOTORCYCLE)])])
        with self.assertRaises(RuntimeError): lot.park(Vehicle("KBB2", VehicleType.SUV))

    def test_hourly_pricing_rounds_up(self):
        lot = make_lot()
        entry = datetime(2026, 1, 1, tzinfo=timezone.utc)
        ticket = lot.park(Vehicle("KCC3", VehicleType.COMPACT), entry)
        receipt = lot.leave(ticket.ticket_id, entry + timedelta(minutes=61))
        self.assertEqual(receipt.duration_hours, 2)
        self.assertEqual(receipt.amount, Decimal("200.00"))

    def test_slot_released_after_exit(self):
        lot = make_lot()
        ticket = lot.park(Vehicle("KDD4", VehicleType.MOTORCYCLE))
        lot.leave(ticket.ticket_id)
        self.assertFalse(next(s for s in lot.floors[0].slots if s.slot_id == ticket.slot_id).occupied)

    def test_duplicate_active_vehicle_rejected(self):
        lot = make_lot()
        lot.park(Vehicle("KEE5", VehicleType.COMPACT))
        with self.assertRaises(ValueError): lot.park(Vehicle("KEE5", VehicleType.COMPACT))

    def test_naive_datetime_rejected(self):
        lot = make_lot()
        with self.assertRaises(ValueError): lot.park(Vehicle("KFF6", VehicleType.MOTORCYCLE), datetime.now())

    def test_ticket_cannot_be_closed_twice(self):
        lot = make_lot()
        ticket = lot.park(Vehicle("KGG7", VehicleType.MOTORCYCLE))
        lot.leave(ticket.ticket_id)
        with self.assertRaises(ValueError): lot.leave(ticket.ticket_id)

if __name__ == "__main__": unittest.main()
