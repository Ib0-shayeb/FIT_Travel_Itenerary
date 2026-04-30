from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Trip Planner Mock API")

# Allow the React frontend to talk to this backend without CORS blocking
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/places")
def get_mock_places(city: str):
    return {
        "city": city,
        "places": [
            {"placeId": "castle_111", "name": "Royal Castle", "category": "Popular", "lat": 52.2479, "lng": 21.0142},
            {"placeId": "gem_222", "name": "Neon Museum", "category": "Hidden Gem", "lat": 52.2486, "lng": 21.0478}
        ]
    }

@app.get("/api/nuances")
def get_mock_nuances(city: str):
    return {
        "city": city,
        "cheatSheet": [
            {"category": "Transport", "tip": "Validate paper tickets upon boarding."},
            {"category": "Dining", "tip": "Tipping 10% is standard in sit-down restaurants."}
        ]
    }

@app.post("/api/trips/optimize")
def optimize_mock_trip(request_data: dict):
    # Extracts the hotel name from the incoming request, defaults to "Hotel" if missing
    hotel_name = request_data.get("hotelStartingPoint", {}).get("name", "Hotel")
    
    return {
        "tripId": "fake_trip_123",
        "dailyRoutes": [
            {
                "dayNumber": 1,
                "totalTimeMinutes": 320,
                "route": [
                    {"step": 1, "name": hotel_name, "isHotel": True},
                    {"step": 2, "name": "Mock Output: National Museum", "travelToNextMins": 15},
                    {"step": 3, "name": "Mock Output: Lazienki Park", "travelToNextMins": 20},
                    {"step": 4, "name": hotel_name, "isHotel": True}
                ]
            }
        ]
    }