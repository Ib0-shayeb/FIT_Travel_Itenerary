import os
import math
import httpx
from typing import List, Dict


class PlacesClient:

    def __init__(self):

        self.api_key = os.getenv("GOOGLE_PLACES_API_KEY")

        self.base_url = (
            "https://places.googleapis.com/v1/places:searchText"
        )

        self.headers = {
            "X-Goog-Api-Key": self.api_key,

            "X-Goog-FieldMask":
                "places.id,"
                "places.displayName.text,"
                "places.rating,"
                "places.userRatingCount,"
                "places.location",

            "Content-Type": "application/json"
        }

    # ---------------------------------------------------
    # TOURIST PLACES
    # ---------------------------------------------------

    async def get_place_recommendations(
        self,
        city: str, medical_nodes: list
    ) -> List[Dict]:

        if not self.api_key:
            return [{"error": "Google API Key missing"}]

        payload = {
            "textQuery": f"top tourist attractions in {city}",
            "languageCode": "en"
        }

        print(f"📡 Searching attractions in {city}")

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

                    print(
                        f"❌ Google API Error: {response.text}"
                    )

                    return [{
                        "error":
                        f"Google API failed ({response.status_code})"
                    }]

                data = response.json()

                raw_places = data.get("places", [])

                return self._format_and_mix_places(
                     city,
                     raw_places,
                      medical_nodes
                     )

        except Exception as e:

            print(f"❌ Network Error: {e}")

            return [{
                "error": "Failed to connect to Google API"
            }]

    # ---------------------------------------------------
    # FORMAT + HIDDEN GEMS
    # ---------------------------------------------------

    def _format_and_mix_places(
        self,
        city: str,
        raw_places: list
    , medical_nodes: list) -> List[Dict]:

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

                "name": place.get(
                    "displayName",
                    {}
                ).get("text", "Unknown"),

                "category": "Popular",

                "rating": place.get("rating", 0.0),

                "reviewVolume": place.get(
                    "userRatingCount",
                    0
                ),
                 "riskLevel": get_risk_level(p_lat, p_lng),

                  "lat": p_lat,
                 "lng": p_lng
            })

        # HIDDEN GEMS

        if city.lower() == "venice":

            gem_lat, gem_lng = 45.4379, 12.3421
            formatted_places.append({
                "id": "v_gem_1",

                "name": "Libreria Acqua Alta",

                "category": "Hidden Gem",
                "rating": 4.8,
                "reviewVolume": 120,
                "riskLevel": get_risk_level(gem_lat, gem_lng), # Added Risk Factor!
                "lat": gem_lat,
                "lng": gem_lng,
            })
            
        return formatted_places

    # ---------------------------------------------------
    # HOTEL SEARCH
    # ---------------------------------------------------

    async def search_hotels(
        self,
        query: str
    ) -> List[Dict]:

        if not self.api_key:
            return []

        payload = {
            "textQuery": f"{query} hotels in Venice",
            "languageCode": "en"
        }

        print(f"🏨 Searching hotels: {query}")

        try:

            async with httpx.AsyncClient() as client:

                response = await client.post(
                    self.base_url,
                    headers=self.headers,
                    json=payload,
                    timeout=8.0
                )

                if response.status_code != 200:

                    print(
                        f"❌ Hotel API Error: {response.text}"
                    )

                    return []

                data = response.json()

                raw_places = data.get("places", [])

                hotels = []

                for place in raw_places[:5]:

                    hotels.append({

                        "placeId": place.get("id"),

                        "name": place.get(
                            "displayName",
                            {}
                        ).get("text", "Unknown Hotel"),

                        "lat": place.get(
                            "location",
                            {}
                        ).get("latitude", 0.0),

                        "lng": place.get(
                            "location",
                            {}
                        ).get("longitude", 0.0),
                    })

                return hotels

        except Exception as e:

            print(f"❌ Hotel Search Error: {e}")

            return []