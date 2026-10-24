from datetime import datetime, timedelta, timezone
from parking import ParkingFloor, ParkingLot, ParkingSlot, SlotType, Vehicle, VehicleType

floor = ParkingFloor(1, [
    ParkingSlot("M-01", SlotType.MOTORCYCLE),
    ParkingSlot("C-01", SlotType.COMPACT),
    ParkingSlot("L-01", SlotType.LARGE),
    ParkingSlot("EV-01", SlotType.EV_CHARGING),
])
lot = ParkingLot([floor])
entry = datetime.now(timezone.utc)
ticket = lot.park(Vehicle("KDA 123A", VehicleType.COMPACT), entry)
receipt = lot.leave(ticket.ticket_id, entry + timedelta(minutes=75))
print("Ticket:", ticket)
print("Receipt:", receipt)
