import os
import math
import httpx
from typing import List, Dict

class PlacesClient:
    def __init__(self):
        self.api_key = os.getenv("GOOGLE_PLACES_API_KEY")
        # We are using the modern Google Places (New) API
        self.base_url = "https://places.googleapis.com/v1/places:searchText"
        
        # Google REQUIRES you to specify exactly which fields you want back to save bandwidth
        self.headers = {
            "X-Goog-Api-Key": f"{self.api_key}",
            "X-Goog-FieldMask": "places.id,places.displayName.text,places.rating,places.userRatingCount,places.location",
            "Content-Type": "application/json"
        }

    async def get_place_recommendations(self, city: str, medical_nodes: list) -> List[Dict]:
        if not self.api_key:
            return [{"error": "Google API Key missing"}]

        # 1. Ask Google for the most popular tourist attractions in the city
        payload = {
            "textQuery": f"top tourist attractions in {city}",
            "languageCode": "en"
        }

        print(f"📡 Sending Request to Google Places for: {city}...")

        try:
            async with httpx.AsyncClient() as client:
                # ---> THIS IS WHAT GOT DELETED! <---
                response = await client.post(
                    self.base_url,
                    headers=self.headers,
                    json=payload,
                    timeout=8.0
                )
                
                if response.status_code != 200:
                    print(f"❌ Google API Error: {response.text}")
                    return [{"error": f"Failed to fetch places. Status {response.status_code}"}]

                data = response.json()
                raw_places = data.get("places", [])
                
                # 2. Format Google's data, mix in our custom Hidden Gems, and calculate RISK!
                return self._format_and_mix_places(city, raw_places, medical_nodes)

        except Exception as e:
            print(f"❌ Network Error: {e}")
            return [{"error": "Failed to connect to Google API"}]

    def _format_and_mix_places(self, city: str, raw_places: list, medical_nodes: list) -> List[Dict]:
        formatted_places = []
        
        # --- Helper function to calculate distance & risk ---
        def get_risk_level(lat, lng):
            if not medical_nodes: 
                return "Unknown"
            
            # Find distance to closest hospital
            shortest_dist = min([
                math.sqrt((lat - node['lat'])**2 + (lng - node['lng'])**2) 
                for node in medical_nodes
            ])
            
            # Assign risk based on coordinate distance thresholds
            if shortest_dist < 0.01: return "Low Risk" 
            if shortest_dist < 0.025: return "Medium Risk"
            return "High Risk"

        # --- 1. Process Google's "Popular" Places ---
        for place in raw_places[:5]: 
            p_lat = place.get("location", {}).get("latitude", 0.0)
            p_lng = place.get("location", {}).get("longitude", 0.0)
            
            formatted_places.append({
                "id": place.get("id"), 
                "name": place.get("displayName", {}).get("text", "Unknown"),
                "category": "Popular",
                "riskLevel": get_risk_level(p_lat, p_lng), # Added Risk Factor!
                "coords": { 
                    "lat": p_lat,
                    "lng": p_lng
                }
            })

        # --- 2. Inject our "Hidden Gems" ---
        if city.lower() == "venice":
            gem_lat, gem_lng = 45.4379, 12.3421
            formatted_places.append({
                "id": "v_gem_1",
                "name": "Libreria Acqua Alta",
                "category": "Hidden Gem",
                "riskLevel": get_risk_level(gem_lat, gem_lng), # Added Risk Factor!
                "coords": { "lat": gem_lat, "lng": gem_lng }
            })
            
        return formatted_places