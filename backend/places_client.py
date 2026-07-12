import os
import math
import httpx
from typing import List, Dict

class PlacesClient:
    def __init__(self):
        self.api_key = os.getenv("GOOGLE_PLACES_API_KEY")
        self.base_url = "https://places.googleapis.com/v1/places:searchText"
        
        self.headers = {
            "X-Goog-Api-Key": f"{self.api_key}",
            "X-Goog-FieldMask": "places.id,places.displayName.text,places.rating,places.userRatingCount,places.location",
            "Content-Type": "application/json"
        }

    async def get_place_recommendations(self, city: str, medical_nodes: list, hidden_gems: list) -> List[Dict]:
        if not self.api_key:
            return [{"error": "Google API Key missing"}]

        payload = {
            "textQuery": f"top tourist attractions in {city}",
            "languageCode": "en"
        }

        print(f"INFO: Querying Google Places API for: {city}")

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.base_url,
                    headers=self.headers,
                    json=payload,
                    timeout=8.0
                )
                
                if response.status_code != 200:
                    print(f"ERROR: Google Places API request failed with status {response.status_code}: {response.text}")
                    return [{"error": f"Failed to fetch places. Status {response.status_code}"}]

                data = response.json()
                raw_places = data.get("places", [])
                
                return self._format_and_mix_places(city, raw_places, medical_nodes, hidden_gems)

        except Exception as e:
            print(f"ERROR: Google Places API connection failure: {e}")
            return [{"error": "Failed to connect to Google API"}]

    def _format_and_mix_places(self, city: str, raw_places: list, medical_nodes: list, hidden_gems: list) -> List[Dict]:
        formatted_places = []
        
        def get_risk_level(lat, lng):
            if not medical_nodes: 
                return "Unknown"
            
            shortest_dist = min([
                math.sqrt((lat - node['lat'])**2 + (lng - node['lng'])**2) 
                for node in medical_nodes
            ])
            
            if shortest_dist < 0.01: 
                return "Low Risk" 
            if shortest_dist < 0.025: 
                return "Medium Risk"
            return "High Risk"

        for place in raw_places[:5]: 
            p_lat = place.get("location", {}).get("latitude", 0.0)
            p_lng = place.get("location", {}).get("longitude", 0.0)
            
            formatted_places.append({
                "id": place.get("id"), 
                "name": place.get("displayName", {}).get("text", "Unknown"),
                "category": "Popular",
                "riskLevel": get_risk_level(p_lat, p_lng), 
                "coords": { 
                    "lat": p_lat,
                    "lng": p_lng
                }
            })

        for gem in hidden_gems:
            gem_lat = gem.get("latitude", 0.0)
            gem_lng = gem.get("longitude", 0.0)
            
            formatted_places.append({
                "id": str(gem.get("id")), 
                "name": gem.get("name", "Unknown Gem"),
                "category": "Hidden Gem",
                "riskLevel": get_risk_level(gem_lat, gem_lng), 
                "coords": { 
                    "lat": gem_lat, 
                    "lng": gem_lng 
                }
            })
            
        return formatted_places