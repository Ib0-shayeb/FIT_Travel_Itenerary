import os
from pydantic import BaseModel
from typing import List
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from typing import List, Optional
import httpx
from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from supabase import create_client, Client

# Load the secret keys from the .env file
load_dotenv()

# --- SUPABASE SETUP ---
# Ensure these two variables are in your .env file!
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if SUPABASE_URL and SUPABASE_KEY:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
else:
    print("⚠️ WARNING: Supabase URL or Key missing. Database calls will fail.")
    supabase = None

# 1. Your External API Clients
from flight_client import FlightClient
from places_client import PlacesClient

# 2. ---> IMPORT FROM YOUR NEW ALGORITHM FILE <---
from route_optimizer import (
    SafeMedicalOptimizer, 
    OptimizeRequest, 
    OptimizeResponse,
    Coordinate,
    MedicalNode
)

# ==========================================
# STARTUP HEALTH CHECK 

# ==========================================
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀 Booting up server... Running health checks.")
    
    duffel_api_key = os.getenv("DUFFEL_API_KEY")
    if not duffel_api_key:
        print("❌ ERROR: DUFFEL_API_KEY is missing from the .env file!")
    else:
        test_api_url = "https://api.duffel.com/air/airlines?limit=1"
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
                    airline_name = data.get("data", [{}])[0].get("name", "Unknown")
                    print(f"✅ Duffel API is ONLINE. Test Query Successful (Found: {airline_name})")
                else:
                    print(f"⚠️ Warning: Duffel API returned status {response.status_code}")
        except Exception as e:
             print(f"❌ ERROR: Duffel API is unreachable! Details: {e}")

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
        try:
            async with httpx.AsyncClient() as client:
                g_res = await client.post(test_google_url, headers=google_headers, json={"textQuery": "Eiffel Tower"}, timeout=5.0)
                if g_res.status_code == 200:
                    print(" Google Places API is ONLINE.")
                else:
                    print(f" Google API rejected our key! Status: {g_res.status_code}")
        except Exception as e:
                print(f" ERROR: Google API is unreachable! Details: {e}")

    yield 
    print(" Server shutting down.")

# ==========================================
# FASTAPI SETUP
# ==========================================
app = FastAPI(title="Trip Planner API", lifespan=lifespan)
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError,
):
    print("VALIDATION ERROR:")
    print(exc.errors())

    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors()},
    )
client = PlacesClient()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==========================================
# API ENDPOINTS
# ==========================================

@app.post("/api/nuances")
def get_mock_nuances(request_data: dict):
    places_visited = request_data.get("selectedPlaces", [])
    dynamic_tips = []
    
    for place in places_visited:
        name = place.get("name", "Unknown Place")
        dynamic_tips.append({
            "category": "Medical/Emergency",
            "tip": f"Keep your medical ID accessible while visiting {name}. Nearest emergency exit is marked in green."
        })
    
    dynamic_tips.append(
        {"category": "Medical/Emergency", "tip": "Emergency Number in Italy is 112. Show your medical ID card if needed."}
    )

    return {"cheatSheet": dynamic_tips}

@app.post("/api/trips/optimize", response_model=OptimizeResponse)
def optimize_trip(request_data: OptimizeRequest):
    print(request_data)

    try:
        if supabase:
            db_response = supabase.table('medical_nodes').select("*").execute()
            live_medical_nodes = db_response.data
        else:
            live_medical_nodes = []
    except Exception as e:
        print(f"❌ Supabase Error during optimization: {e}")
        live_medical_nodes = []

    medical_models = [
        MedicalNode(
            id=str(node.get('id', '')),
            name=node.get('name', 'Unknown'),
            facility_type=node.get('facility_type', 'Hospital'),
            lat=node.get('lat', 0.0),
            lng=node.get('lng', 0.0),
            is_24_7=node.get('is_24_7', True),
            local_phone=node.get('local_phone', ''),
            emergency_dispatch=node.get('emergency_dispatch', '112')
        ) for node in live_medical_nodes
    ]

    optimizer = SafeMedicalOptimizer()

    final_response = optimizer.calculate_route(
        trip_duration_days=request_data.days,
        hotel=request_data.hotel,
        places=request_data.places,
        medical_nodes=medical_models
    )

    return final_response


# --- RECOMMENDATION ENDPOINTS ---
@app.post("/api/recommendations/places")
async def get_recommended_places(request_data: dict):

    interests = request_data.get("interests", [])
    preferences = request_data.get("preferences", {})

    print("INTERESTS:", interests)
    print("PREFERENCES:", preferences)

    interest_queries = {
        "Food": "best restaurants in Venice",
        "History": "historical places in Venice",
        "Art": "art museums in Venice",
        "Nature": "parks and nature in Venice",
        "Shopping": "shopping centers in Venice",
        "Nightlife": "nightlife bars in Venice",
    }

    live_medical_nodes = []

    all_places = []
    for interest in interests:
        if interest in interest_queries:
            places_for_interest = await client.get_place_recommendations(
                interest_queries[interest], live_medical_nodes
            )
            all_places.extend(places_for_interest)

    # Duplicate'leri temizle
    seen_ids = set()
    live_places = []
    for place in all_places:
        if place.get("id") not in seen_ids:
            seen_ids.add(place.get("id"))
            live_places.append(place)

    # Hiç interest seçilmediyse default
    if not live_places:
        live_places = await client.get_place_recommendations(
            "tourist attractions in Venice", live_medical_nodes
        )

    filtered_places = live_places

    if preferences.get("asthmaFriendly"):
        filtered_places = [
            place for place in filtered_places
            if "bar" not in place.get("name", "").lower()
        ]

    if preferences.get("lowWalking"):
        filtered_places = filtered_places[:3]

    if preferences.get("avoidCrowds"):
        filtered_places = [
            place for place in filtered_places
            if place.get("reviewVolume", 0) < 5000
        ]

    if preferences.get("elderlyFriendly"):
        filtered_places = filtered_places[:4]

    return {
        "city": "Venice",
        "places": filtered_places
    }
@app.get("/api/recommendations/flights")
async def get_recommended_flights(
    origin: str = "LHR",          
    destination: str = "VCE",     
    date: str = "2026-08-15",     
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
async def get_hotels(query: str = ""):

    hotels = await client.search_hotels(query)
     
     
     
    print("HOTELS FOUND:", hotels)

    return {
        "hotels": hotels
    }
from pydantic import BaseModel
from typing import List


class Place(BaseModel):
    id: str
    name: str
    lat: float
    lng: float


class RouteRequest(BaseModel):
    selected_places: List[Place]


@app.post("/optimize-route")
async def optimize_route(data: RouteRequest):

    print("ROUTE REQUEST:")
    print(data)

    return {
        "optimized_route": data.selected_places
    }

@app.get("/api/medical-nodes", response_model=List[MedicalNode])
def get_medical_nodes():
    try:
        # Fetch all rows from the 'medical_nodes' table
        response = supabase.table('medical_nodes').select("*").execute()
        return response.data
    except Exception as e:
        print(f"❌ Supabase Error: {e}")
        return [] # Return an empty list if the database fails so the app doesn't crash
    live_medical_nodes =  get_medical_nodes()