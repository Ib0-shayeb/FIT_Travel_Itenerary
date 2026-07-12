import os
from contextlib import asynccontextmanager
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
import httpx

from supabase import create_client, Client
from flight_client import FlightClient
from places_client import PlacesClient
from route_optimizer import (
    SafeMedicalOptimizer, 
    OptimizeRequest, 
    OptimizeResponse,
    Coordinate,
    MedicalNode
)

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if SUPABASE_URL and SUPABASE_KEY:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
else:
    print("WARNING: Supabase URL or Key missing. Database operations will fail.")


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("INFO: Initializing server health checks.")
    
    duffel_api_key = os.getenv("DUFFEL_API_KEY")
    if not duffel_api_key:
        print("ERROR: DUFFEL_API_KEY is missing from environment.")
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
                    print(f"INFO: Duffel API integration verified. Sample airline: {airline_name}")
                else:
                    print(f"WARNING: Duffel API returned status {response.status_code}")
        except Exception as e:
             print(f"ERROR: Duffel API unreachable. Details: {e}")

    google_api_key = os.getenv("GOOGLE_PLACES_API_KEY")
    if not google_api_key:
        print("ERROR: GOOGLE_PLACES_API_KEY is missing from environment.")
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
                    print("INFO: Google Places API integration verified.")
                else:
                    print(f"ERROR: Google Places API authentication failed. Status: {g_res.status_code}")
        except Exception as e:
                print(f"ERROR: Google Places API unreachable. Details: {e}")

    yield 
    print("INFO: Server shutting down.")


app = FastAPI(title="Trip Planner API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_methods=["*"],
    allow_headers=["*"],
)


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
    try:
        db_response = supabase.table('medical_nodes').select("*").execute()
        live_medical_nodes = db_response.data
    except Exception as e:
        print(f"ERROR: Supabase query failure during optimization: {e}")
        live_medical_nodes = []
    
    medical_models = [
        MedicalNode(
            id=str(node.get('id', '')), 
            name=node.get('name', 'Unknown Medical Node'), 
            facility_type=node.get('facility_type', 'Hospital'),
            lat=node.get('lat', 0.0), 
            lng=node.get('lng', 0.0), 
            is_24_7=node.get('is_24_7', True), 
            local_phone=node.get('local_phone', ''), 
            emergency_dispatch=node.get('emergency_dispatch', '112')
        ) for node in live_medical_nodes
    ]
    
    optimizer = SafeMedicalOptimizer()
    return optimizer.calculate_route(
        trip_duration_days=request_data.days,
        hotel=request_data.hotel,
        places=request_data.places,
        medical_nodes=medical_models
    )


@app.get("/api/recommendations/places")
async def get_recommended_places(city: str = "Venice"):
    try:
        db_nodes = supabase.table('medical_nodes').select("*").execute()
        live_medical_nodes = db_nodes.data
    except Exception as e:
        print(f"ERROR: Supabase query failure (medical_nodes): {e}")
        live_medical_nodes = []
        
    try:
        db_gems = supabase.table('underrated_places').select("*").execute()
        live_hidden_gems = db_gems.data
    except Exception as e:
        print(f"ERROR: Supabase query failure (underrated_places): {e}")
        live_hidden_gems = []
        
    client = PlacesClient()
    live_places = await client.get_place_recommendations(
        city, 
        live_medical_nodes, 
        live_hidden_gems
    )
    return {
        "city": city,
        "places": live_places
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
def get_recommended_hotels():
    return {
        "destination": "Venice",
        "hotels": [
            {
                "hotelId": "hot_111",
                "name": "Hotel Danieli (Verified Safe Zone)",
                "pricePerNight": "€450",
                "lat": 45.4337,
                "lng": 12.3421,
                "verifiedLodgingScore": 9.5,
                "safetyStatus": "Immediate Proximity to Emergency Transport",
                "externalBookingLink": "https://www.booking.com/hotel/it/danieli-venice.html"
            },
            {
                "hotelId": "hot_222",
                "name": "Belmond Hotel Cipriani",
                "pricePerNight": "€800",
                "lat": 45.4239,
                "lng": 12.3384,
                "verifiedLodgingScore": 9.8,
                "safetyStatus": "On-Site Medical Staff",
                "externalBookingLink": "https://www.booking.com/hotel/it/belmond-cipriani.html"
            }
        ]
    }


@app.get("/api/medical-nodes", response_model=List[MedicalNode])
def get_medical_nodes():
    try:
        response = supabase.table('medical_nodes').select("*").execute()
        return response.data
    except Exception as e:
        print(f"ERROR: Supabase query failure: {e}")
        return []