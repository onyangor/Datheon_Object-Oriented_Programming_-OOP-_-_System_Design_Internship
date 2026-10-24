# Smart Parking Lot — UML

```mermaid
classDiagram
    class ParkingLot {
      -floors: list[ParkingFloor]
      -pricing: PricingStrategy
      -active: dict
      +park(vehicle, entry_time) ParkingTicket
      +leave(ticket_id, exit_time) ParkingReceipt
    }
    class ParkingFloor {
      +floor_number: int
      +slots: tuple[ParkingSlot]
    }
    class ParkingSlot {
      +slot_id: str
      +slot_type: SlotType
      +occupied: bool
      +can_fit(vehicle) bool
      +reserve(ticket_id, vehicle) bool
      +release(ticket_id) bool
    }
    class Vehicle {
      +plate: str
      +vehicle_type: VehicleType
      +electric: bool
    }
    class ParkingTicket {
      +ticket_id: str
      +vehicle_plate: str
      +floor_number: int
      +slot_id: str
      +entry_time: datetime
    }
    class ParkingReceipt {
      +ticket: ParkingTicket
      +exit_time: datetime
      +duration_hours: int
      +amount: Decimal
    }
    class PricingStrategy {
      <<abstract>>
      +calculate(vehicle, hours) Decimal
    }
    class HourlyPricing {
      +calculate(vehicle, hours) Decimal
    }
    ParkingLot "1" *-- "1..*" ParkingFloor
    ParkingFloor "1" *-- "1..*" ParkingSlot
    ParkingLot --> PricingStrategy
    PricingStrategy <|.. HourlyPricing
    ParkingLot ..> Vehicle
    ParkingLot ..> ParkingTicket
    ParkingLot ..> ParkingReceipt
```

## Allocation rule
First-fit: scan floors in ascending configured order and each floor's slots in configured order. A slot is reserved atomically under its own lock. The lot-level lock prevents duplicate active vehicle tickets and coordinates allocation/checkout in this in-memory model.
