import os
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

    async def get_place_recommendations(self, city: str) -> List[Dict]:
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
                
                # 2. Format Google's data and mix in our custom Hidden Gems!
                return self._format_and_mix_places(city, raw_places)

        except Exception as e:
            print(f"❌ Network Error: {e}")
            return [{"error": "Failed to connect to Google API"}]

    def _format_and_mix_places(self, city: str, raw_places: list) -> List[Dict]:
        formatted_places = []
        
        # --- 1. Process Google's "Popular" Places ---
        # Let's just take the top 5 to keep the UI clean
        for place in raw_places[:5]: 
            formatted_places.append({
                "placeId": place.get("id"),
                "name": place.get("displayName", {}).get("text", "Unknown"),
                "category": "Popular",
                "rating": place.get("rating", 0.0),
                "reviewVolume": place.get("userRatingCount", 0),
                "lat": place.get("location", {}).get("latitude", 0.0),
                "lng": place.get("location", {}).get("longitude", 0.0)
            })

        # --- 2. Inject our "Hidden Gems" from the Report ---
        # Later, your Data Manager will pull these from Supabase. 
        # For now, we hardcode them to prove the concept works.
        if city.lower() == "vienna":
            formatted_places.append({
                "placeId": "v_gem_1",
                "name": "Hundertwasserhaus",
                "category": "Hidden Gem",
                "rating": 4.6,
                "reviewVolume": 1200,
                "lat": 48.2077,
                "lng": 16.3939
            })
            formatted_places.append({
                "placeId": "v_gem_2",
                "name": "Krypt Bar (Secret Underground Vault)",
                "category": "Hidden Gem",
                "rating": 4.8,
                "reviewVolume": 450,
                "lat": 48.2144,
                "lng": 16.3615
            })

        return formatted_places