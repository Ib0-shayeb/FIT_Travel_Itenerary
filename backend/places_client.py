import os
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
        city: str
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
                    raw_places
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
    ) -> List[Dict]:

        formatted_places = []

        # GOOGLE RESULTS

        for place in raw_places[:5]:

            formatted_places.append({
                "placeId": place.get("id"),

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

                "lat": place.get(
                    "location",
                    {}
                ).get("latitude", 0.0),

                "lng": place.get(
                    "location",
                    {}
                ).get("longitude", 0.0)
            })

        # HIDDEN GEMS

        if city.lower() == "venice":

            formatted_places.append({
                "placeId": "v_gem_1",

                "name": "Libreria Acqua Alta",

                "category": "Hidden Gem",

                "rating": 4.7,

                "reviewVolume": 8500,

                "lat": 45.4379,

                "lng": 12.3421
            })

            formatted_places.append({
                "placeId": "v_gem_2",

                "name": "Scala Contarini del Bovolo",

                "category": "Hidden Gem",

                "rating": 4.6,

                "reviewVolume": 2100,

                "lat": 45.4348,

                "lng": 12.3346
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