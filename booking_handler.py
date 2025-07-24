from dataclasses import dataclass
from typing import Dict, List, Optional
import json

@dataclass
class BookingItem:
    type: str  # flight, hotel, activity
    name: str
    date: str
    price: float
    details: Dict
    booking_reference: Optional[str] = None

class BookingHandler:
    def __init__(self):
        self.bookings = []
        self.total_cost = 0.0
    
    def add_booking(self, item: BookingItem) -> str:
        """Add a booking item to the cart"""
        # Generate a simple booking reference
        booking_ref = f"{item.type.upper()}-{len(self.bookings) + 1:04d}"
        item.booking_reference = booking_ref
        
        self.bookings.append(item)
        self.total_cost += item.price
        
        return booking_ref
    
    def remove_booking(self, booking_reference: str) -> bool:
        """Remove a booking by reference"""
        for i, booking in enumerate(self.bookings):
            if booking.booking_reference == booking_reference:
                self.total_cost -= booking.price
                del self.bookings[i]
                return True
        return False
    
    def get_booking_summary(self) -> Dict:
        """Get a summary of all bookings"""
        summary = {
            "total_items": len(self.bookings),
            "total_cost": self.total_cost,
            "bookings": []
        }
        
        for booking in self.bookings:
            summary["bookings"].append({
                "reference": booking.booking_reference,
                "type": booking.type,
                "name": booking.name,
                "date": booking.date,
                "price": booking.price,
                "details": booking.details
            })
        
        return summary
    
    def simulate_booking(self) -> Dict:
        """Simulate the booking process (in real app, this would connect to actual booking APIs)"""
        if not self.bookings:
            return {"success": False, "message": "No items to book"}
        
        # Simulate booking process
        booking_results = []
        for booking in self.bookings:
            # In a real application, you would integrate with actual booking APIs
            result = {
                "reference": booking.booking_reference,
                "status": "confirmed",
                "confirmation_code": f"CONF-{booking.booking_reference}",
                "message": f"{booking.type.title()} booking confirmed"
            }
            booking_results.append(result)
        
        return {
            "success": True,
            "total_cost": self.total_cost,
            "bookings": booking_results,
            "message": f"Successfully booked {len(self.bookings)} items"
        }