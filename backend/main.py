from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Trip Planner Mock API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- ORIGINAL ENDPOINTS ---

@app.post("/api/nuances")
def get_mock_nuances(request_data: dict):
    # Extract the list of places the frontend sent
    places_visited = request_data.get("selectedPlaces", [])
    
    # Create a dynamic mock response based on what they sent
    dynamic_tips = []
    
    for place in places_visited:
        name = place.get("name", "Unknown Place")
        dynamic_tips.append({
            "category": "Attraction Specific",
            "tip": f"Mock Rule: Remember to check the specific dress code and entry requirements for {name}."
        })
    
    # Add some general transport rules that always apply
    dynamic_tips.append(
        {"category": "Transport", "tip": "Validate paper tickets upon boarding the U-Bahn."}
    )

    return {
        "cheatSheet": dynamic_tips
    }

@app.post("/api/trips/optimize")
def optimize_mock_trip(request_data: dict):
    hotel_name = request_data.get("hotelStartingPoint", {}).get("name", "Hotel")
    return {
        "tripId": "fake_trip_123",
        "dailyRoutes": [
            {
                "dayNumber": 1,
                "totalTimeMinutes": 320,
                "route": [
                    {"step": 1, "name": hotel_name, "isHotel": True},
                    {"step": 2, "name": "Mock Output: Schönbrunn Palace", "travelToNextMins": 25},
                    {"step": 3, "name": "Mock Output: Hundertwasserhaus", "travelToNextMins": 15},
                    {"step": 4, "name": hotel_name, "isHotel": True}
                ]
            }
        ]
    }

# --- NEW RECOMMENDATION ENDPOINTS ---

@app.get("/api/recommendations/places")
def get_recommended_places():
    return {
        "city": "Vienna",
        "places": [
            {
                "placeId": "v_pop_1",
                "name": "Schönbrunn Palace",
                "category": "Popular",
                "rating": 4.8,
                "reviewVolume": 45000,
                "lat": 48.1848,
                "lng": 16.3122
            },
            {
                "placeId": "v_gem_1",
                "name": "Hundertwasserhaus",
                "category": "Hidden Gem",
                "rating": 4.6,
                "reviewVolume": 1200,
                "lat": 48.2077,
                "lng": 16.3939
            }
        ]
    }

@app.get("/api/recommendations/flights")
def get_recommended_flights():
    return {
        "destination": "Vienna",
        "flights": [
            {
                "flightId": "FR1234",
                "airline": "Ryanair",
                "priceEstimate": "€45",
                "insights": {
                    "price": "Very low",
                    "comfort": "Low, basic but acceptable for short flights",
                    "service": "Generally friendly but limited service",
                    "baggagePolicy": "Strict but clear rules",
                    "reliability": "Often punctual"
                }
            },
            {
                "flightId": "LO555",
                "airline": "LOT Polish Airlines",
                "priceEstimate": "€85",
                "insights": {
                    "price": "Low prices",
                    "comfort": "Medium-low depends on the aircraft",
                    "service": "Sometimes professional, sometimes unresponsive",
                    "baggagePolicy": "Issues reported",
                    "reliability": "Delays and cancellations reported"
                }
            }
        ]
    }

@app.get("/api/recommendations/hotels")
def get_recommended_hotels():
    return {
        "destination": "Vienna",
        "hotels": [
            {
                "hotelId": "hot_111",
                "name": "Motel One Wien-Staatsoper",
                "pricePerNight": "€120",
                "lat": 48.2023,
                "lng": 16.3688,
                "verifiedLodgingScore": 9.2,
                "safetyStatus": "Verified Safe Area",
                "externalBookingLink": "https://www.booking.com/hotel/at/motel-one-wien-staatsoper.html"
            },
            {
                "hotelId": "hot_222",
                "name": "Boutique Hotel am Stephansplatz",
                "pricePerNight": "€210",
                "lat": 48.2082,
                "lng": 16.3719,
                "verifiedLodgingScore": 9.6,
                "safetyStatus": "Verified Safe Area",
                "externalBookingLink": "https://www.booking.com/hotel/at/boutique-hotel-am-stephansplatz.html"
            }
        ]
    }