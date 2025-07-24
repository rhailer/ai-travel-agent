import os
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

@dataclass
class TravelPreferences:
    destination: str
    departure_date: str
    return_date: str
    budget: float
    travelers: int
    accommodation_type: str
    activities: List[str]
    dietary_restrictions: List[str] = None

@dataclass
class TravelPlan:
    destination: str
    itinerary: List[Dict]
    accommodation_suggestions: List[Dict]
    flight_suggestions: List[Dict]
    estimated_cost: float
    recommendations: List[str]

class TravelAgent:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        if not os.getenv("OPENAI_API_KEY"):
            raise ValueError("OpenAI API key not found. Please set OPENAI_API_KEY in your .env file")
    
    def validate_preferences(self, preferences: TravelPreferences) -> List[str]:
        """Validate user preferences and return any errors"""
        errors = []
        
        try:
            departure = datetime.strptime(preferences.departure_date, "%Y-%m-%d")
            return_date = datetime.strptime(preferences.return_date, "%Y-%m-%d")
            
            if departure < datetime.now():
                errors.append("Departure date cannot be in the past")
            
            if return_date <= departure:
                errors.append("Return date must be after departure date")
                
        except ValueError:
            errors.append("Please use YYYY-MM-DD format for dates")
        
        if preferences.budget <= 0:
            errors.append("Budget must be greater than 0")
        
        if preferences.travelers <= 0:
            errors.append("Number of travelers must be at least 1")
        
        if not preferences.destination.strip():
            errors.append("Destination cannot be empty")
            
        return errors
    
    def create_travel_plan(self, preferences: TravelPreferences) -> TravelPlan:
        """Generate a comprehensive travel plan using OpenAI"""
        
        # Validate input
        validation_errors = self.validate_preferences(preferences)
        if validation_errors:
            raise ValueError(f"Validation errors: {', '.join(validation_errors)}")
        
        # Calculate trip duration
        departure = datetime.strptime(preferences.departure_date, "%Y-%m-%d")
        return_date = datetime.strptime(preferences.return_date, "%Y-%m-%d")
        duration = (return_date - departure).days
        
        prompt = f"""
        Create a detailed travel plan for the following trip:
        
        Destination: {preferences.destination}
        Departure: {preferences.departure_date}
        Return: {preferences.return_date}
        Duration: {duration} days
        Budget: ${preferences.budget} USD
        Travelers: {preferences.travelers}
        Accommodation Type: {preferences.accommodation_type}
        Preferred Activities: {', '.join(preferences.activities)}
        Dietary Restrictions: {', '.join(preferences.dietary_restrictions or ['None'])}
        
        Please provide a JSON response with the following structure:
        {{
            "itinerary": [
                {{
                    "day": 1,
                    "date": "YYYY-MM-DD",
                    "activities": ["activity1", "activity2"],
                    "meals": ["breakfast location", "lunch location", "dinner location"],
                    "estimated_cost": 150.00
                }}
            ],
            "accommodation_suggestions": [
                {{
                    "name": "Hotel Name",
                    "type": "hotel/airbnb/hostel",
                    "price_per_night": 120.00,
                    "rating": 4.5,
                    "location": "City Center",
                    "amenities": ["wifi", "breakfast", "pool"]
                }}
            ],
            "flight_suggestions": [
                {{
                    "route": "Origin - Destination",
                    "departure_time": "2024-01-15 08:00",
                    "arrival_time": "2024-01-15 12:00",
                    "estimated_price": 450.00,
                    "airline": "Airline Name"
                }}
            ],
            "estimated_total_cost": 2500.00,
            "recommendations": [
                "Book flights early for better prices",
                "Consider travel insurance",
                "Check visa requirements"
            ]
        }}
        
        Make sure all suggestions fit within the specified budget and preferences.
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert travel agent. Provide detailed, practical, and budget-conscious travel plans in valid JSON format."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=2000
            )
            
            # Parse the response
            plan_data = json.loads(response.choices[0].message.content)
            
            return TravelPlan(
                destination=preferences.destination,
                itinerary=plan_data.get("itinerary", []),
                accommodation_suggestions=plan_data.get("accommodation_suggestions", []),
                flight_suggestions=plan_data.get("flight_suggestions", []),
                estimated_cost=plan_data.get("estimated_total_cost", 0),
                recommendations=plan_data.get("recommendations", [])
            )
            
        except json.JSONDecodeError:
            raise ValueError("Failed to parse travel plan. Please try again.")
        except Exception as e:
            raise ValueError(f"Error generating travel plan: {str(e)}")
    
    def get_travel_tips(self, destination: str) -> List[str]:
        """Get specific travel tips for the destination"""
        
        prompt = f"""
        Provide 10 essential travel tips for visiting {destination}. 
        Include practical advice about:
        - Local customs and etiquette
        - Safety considerations
        - Money and payments
        - Transportation
        - Best time to visit
        - What to pack
        - Local cuisine recommendations
        - Cultural attractions
        - Language tips
        - Emergency contacts
        
        Format as a simple list of tips.
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a knowledgeable travel expert providing practical advice."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5,
                max_tokens=800
            )
            
            tips = response.choices[0].message.content.strip().split('\n')
            return [tip.strip('- ').strip() for tip in tips if tip.strip()]
            
        except Exception as e:
            return [f"Error getting travel tips: {str(e)}"]