import os
from flight_client import FlightClient
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from places_client import PlacesClient
import httpx

# Load the secret keys from the .env file
load_dotenv()

# ==========================================
# 1. STARTUP HEALTH CHECK (DUFFEL API)
# ==========================================
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀 Booting up server... Running health checks.")
    
    # Securely grab the API key
    duffel_api_key = os.getenv("DUFFEL_API_KEY")
    
    if not duffel_api_key:
        print("❌ ERROR: DUFFEL_API_KEY is missing from the .env file!")
    else:
        # Test query: Ask Duffel for a list of airlines, limited to 1 just to prove auth works
        test_api_url = "https://api.duffel.com/air/airlines?limit=1"
        
        # Duffel requires these exact headers
        headers = {
            "Authorization": f"Bearer {duffel_api_key}",
            "Duffel-Version": "v2",
            "Accept": "application/json"
        } 
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(test_api_url, headers=headers, timeout=5.0)
                
                if response.status_code == 200:
                    data = response.json()
                    # Grab the airline name from the response to prove it worked
                    airline_name = data.get("data", [{}])[0].get("name", "Unknown")
                    print(f"✅ Duffel API is ONLINE. Test Query Successful (Found: {airline_name})")
                elif response.status_code == 401:
                    print("❌ ERROR: Duffel API rejected our key! Check your .env file.")
                else:
                    print(f"⚠️ Warning: Duffel API returned status {response.status_code}")
                    print(f"🔍 Duffel Error Message: {response.text}")
                    
        except Exception as e:
             print(f"❌ ERROR: Duffel API is unreachable! Details: {e}")

    yield 
    print("🛑 Server shutting down.")

    # --- GOOGLE PLACES HEALTH CHECK ---
    google_api_key = os.getenv("GOOGLE_PLACES_API_KEY")
    if not google_api_key:
        print("❌ ERROR: GOOGLE_PLACES_API_KEY is missing from the .env file!")
    else:
        test_google_url = "https://places.googleapis.com/v1/places:searchText"
        google_headers = {
            "X-Goog-Api-Key": google_api_key,
            "X-Goog-FieldMask": "places.displayName.text",
            "Content-Type": "application/json"
        }
        # We just ask for 1 place to prove the key works
        try:
            async with httpx.AsyncClient() as client:
                g_res = await client.post(test_google_url, headers=google_headers, json={"textQuery": "Eiffel Tower"}, timeout=5.0)
                if g_res.status_code == 200:
                    print("✅ Google Places API is ONLINE.")
                else:
                    print(f"❌ Google API rejected our key! Status: {g_res.status_code}")
        except Exception as e:
                print(f"❌ ERROR: Google API is unreachable! Details: {e}")

# ==========================================
# 2. FASTAPI SETUP
# ==========================================
app = FastAPI(title="Trip Planner API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_methods=["*"],
    allow_headers=["*"],
)

# ... (Keep all your existing @app.get and @app.post routes below here)

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
async def get_recommended_places(city: str = "Vienna"):
    client = PlacesClient()

    live_places = await client.get_place_recommendations(city)

    return {
        "city": city,
        "places": live_places
    }

@app.get("/api/recommendations/flights")
async def get_recommended_flights(
    origin: str = "LHR",          # Default to London
    destination: str = "VIE",     # Default to Vienna
    date: str = "2026-08-15",     # Use a future YYYY-MM-DD date
    adults: int = 1,
    children: int = 0
):
    client = FlightClient()
    
    live_flights = await client.get_flight_recommendations(
        origin_code=origin,
        destination_code=destination,
        departure_date=date,
        adults=adults,
        children=children
    )
    
    return {
        "search_parameters": {
            "origin": origin,
            "destination": destination,
            "date": date,
            "passengers": adults + children
        },
        "flights": live_flights
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