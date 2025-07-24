import streamlit as st
from datetime import datetime, timedelta
from travel_agent import TravelAgent, TravelPreferences
from booking_handler import BookingHandler, BookingItem

# Initialize session state
if 'travel_agent' not in st.session_state:
    try:
        st.session_state.travel_agent = TravelAgent()
    except ValueError as e:
        st.error(f"Configuration error: {e}")
        st.stop()

if 'booking_handler' not in st.session_state:
    st.session_state.booking_handler = BookingHandler()

if 'travel_plan' not in st.session_state:
    st.session_state.travel_plan = None

# App configuration
st.set_page_config(
    page_title="AI Travel Agent",
    page_icon="✈️",
    layout="wide"
)

st.title("🌍 AI Travel Agent")
st.subheader("Plan and book your perfect trip with AI assistance")

# Sidebar for trip preferences
st.sidebar.header("Trip Preferences")

with st.sidebar.form("trip_preferences"):
    destination = st.text_input("Destination", placeholder="e.g., Paris, France")
    
    col1, col2 = st.columns(2)
    with col1:
        departure_date = st.date_input(
            "Departure", 
            min_value=datetime.now().date(),
            value=datetime.now().date() + timedelta(days=30)
        )
    with col2:
        return_date = st.date_input(
            "Return", 
            min_value=datetime.now().date() + timedelta(days=1),
            value=datetime.now().date() + timedelta(days=37)
        )
    
    budget = st.number_input("Budget (USD)", min_value=100, value=2000, step=100)
    travelers = st.number_input("Number of Travelers", min_value=1, value=2, step=1)
    
    accommodation_type = st.selectbox(
        "Accommodation Type",
        ["Hotel", "Airbnb", "Hostel", "Resort", "Bed & Breakfast"]
    )
    
    activities = st.multiselect(
        "Preferred Activities",
        ["Sightseeing", "Museums", "Food Tours", "Nightlife", "Shopping", 
         "Adventure Sports", "Beach Activities", "Cultural Events", "Nature/Hiking"]
    )
    
    dietary_restrictions = st.multiselect(
        "Dietary Restrictions",
        ["Vegetarian", "Vegan", "Gluten-Free", "Halal", "Kosher", "No Restrictions"]
    )
    
    submitted = st.form_submit_button("Generate Travel Plan")

# Main content area
if submitted and destination:
    with st.spinner("Creating your personalized travel plan..."):
        try:
            preferences = TravelPreferences(
                destination=destination,
                departure_date=departure_date.strftime("%Y-%m-%d"),
                return_date=return_date.strftime("%Y-%m-%d"),
                budget=budget,
                travelers=int(travelers),
                accommodation_type=accommodation_type.lower(),
                activities=activities,
                dietary_restrictions=dietary_restrictions
            )
            
            st.session_state.travel_plan = st.session_state.travel_agent.create_travel_plan(preferences)
            st.success("Travel plan generated successfully!")
            
        except Exception as e:
            st.error(f"Error generating travel plan: {e}")

# Display travel plan
if st.session_state.travel_plan:
    plan = st.session_state.travel_plan
    
    # Plan overview
    st.header(f"Travel Plan: {plan.destination}")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Estimated Total Cost", f"${plan.estimated_cost:,.2f}")
    with col2:
        st.metric("Duration", f"{len(plan.itinerary)} days")
    with col3:
        st.metric("Activities Planned", sum(len(day.get('activities', [])) for day in plan.itinerary))
    
    # Tabs for different sections
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["📅 Itinerary", "🏨 Accommodation", "✈️ Flights", "💡 Recommendations", "🎯 Travel Tips"])
    
    with tab1:
        st.subheader("Daily Itinerary")
        for day in plan.itinerary:
            with st.expander(f"Day {day['day']} - {day.get('date', '')}"):
                st.write("**Activities:**")
                for activity in day.get('activities', []):
                    st.write(f"• {activity}")
                
                st.write("**Meals:**")
                for meal in day.get('meals', []):
                    st.write(f"• {meal}")
                
                st.write(f"**Estimated Daily Cost:** ${day.get('estimated_cost', 0):.2f}")
    
    with tab2:
        st.subheader("Accommodation Suggestions")
        for i, hotel in enumerate(plan.accommodation_suggestions):
            col1, col2 = st.columns([3, 1])
            with col1:
                st.write(f"**{hotel['name']}**")
                st.write(f"Type: {hotel['type'].title()} | Rating: ⭐ {hotel.get('rating', 'N/A')}")
                st.write(f"Location: {hotel.get('location', 'N/A')}")
                st.write(f"Amenities: {', '.join(hotel.get('amenities', []))}")
                st.write(f"**${hotel['price_per_night']:.2f}/night**")
            
            with col2:
                if st.button(f"Add to Booking", key=f"hotel_{i}"):
                    booking_item = BookingItem(
                        type="hotel",
                        name=hotel['name'],
                        date=departure_date.strftime("%Y-%m-%d"),
                        price=hotel['price_per_night'] * len(plan.itinerary),
                        details=hotel
                    )
                    ref = st.session_state.booking_handler.add_booking(booking_item)
                    st.success(f"Added to booking cart! Reference: {ref}")
            
            st.divider()
    
    with tab3:
        st.subheader("Flight Suggestions")
        for i, flight in enumerate(plan.flight_suggestions):
            col1, col2 = st.columns([3, 1])
            with col1:
                st.write(f"**{flight['route']}**")
                st.write(f"Airline: {flight.get('airline', 'N/A')}")
                st.write(f"Departure: {flight.get('departure_time', 'N/A')}")
                st.write(f"Arrival: {flight.get('arrival_time', 'N/A')}")
                st.write(f"**${flight['estimated_price']:.2f}**")
            
            with col2:
                if st.button(f"Add to Booking", key=f"flight_{i}"):
                    booking_item = BookingItem(
                        type="flight",
                        name=f"Flight - {flight['route']}",
                        date=flight.get('departure_time', ''),
                        price=flight['estimated_price'],
                        details=flight
                    )
                    ref = st.session_state.booking_handler.add_booking(booking_item)
                    st.success(f"Added to booking cart! Reference: {ref}")
            
            st.divider()
    
    with tab4:
        st.subheader("Travel Recommendations")
        for rec in plan.recommendations:
            st.write(f"💡 {rec}")
    
    with tab5:
        st.subheader("Travel Tips")
        if st.button("Get Travel Tips"):
            with st.spinner("Getting travel tips..."):
                tips = st.session_state.travel_agent.get_travel_tips(plan.destination)
                for tip in tips:
                    st.write(f"🎯 {tip}")

# Booking cart sidebar
with st.sidebar:
    st.header("🛒 Booking Cart")
    
    booking_summary = st.session_state.booking_handler.get_booking_summary()
    
    if booking_summary['total_items'] > 0:
        st.write(f"**Items: {booking_summary['total_items']}**")
        st.write(f"**Total: ${booking_summary['total_cost']:.2f}**")
        
        for booking in booking_summary['bookings']:
            st.write(f"• {booking['name']}")
            st.write(f"  ${booking['price']:.2f}")
            if st.button(f"Remove", key=f"remove_{booking['reference']}"):
                if st.session_state.booking_handler.remove_booking(booking['reference']):
                    st.success("Item removed!")
                    st.experimental_rerun()
        
        if st.button("📋 Proceed to Booking", type="primary"):
            with st.spinner("Processing booking..."):
                result = st.session_state.booking_handler.simulate_booking()
                if result['success']:
                    st.success("🎉 Booking confirmed!")
                    st.json(result)
                else:
                    st.error(result['message'])
    else:
        st.write("Cart is empty")

# Footer
st.markdown("---")
st.markdown("*This is a demo application. Actual bookings require integration with real travel booking APIs.*")