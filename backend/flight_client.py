import os
import httpx
from datetime import datetime, timedelta
from typing import List, Dict

class FlightClient:
    def __init__(self):
        self.api_key = os.getenv("DUFFEL_API_KEY")
        self.base_url = "https://api.duffel.com/air"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Duffel-Version": "v2",
            "Accept": "application/json",
            "Content-Type": "application/json"
        }

    async def get_flight_recommendations(
        self, 
        origin_code: str, 
        destination_code: str, 
        departure_date: str, 
        adults: int, 
        children: int
    ) -> List[Dict]:
        if not self.api_key:
            return [{"error": "API Key missing"}]

        passengers = [{"type": "adult"} for _ in range(adults)]
        for _ in range(children):
            passengers.append({"age": 10})

        payload = {
            "data": {
                "passengers": passengers,
                "slices": [
                    {
                        "origin": origin_code.upper(),
                        "destination": destination_code.upper(),
                        "departure_date": departure_date
                    }
                ],
                "return_offers": True 
            }
        }

        print(f"INFO: Querying Duffel API: {origin_code.upper()} -> {destination_code.upper()} ({departure_date})")

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/offer_requests",
                    headers=self.headers,
                    json=payload,
                    timeout=10.0
                )
                
                if response.status_code not in (200, 201):
                    print(f"ERROR: Duffel API request failed with status {response.status_code}: {response.text}")
                    return [{"error": f"Failed to fetch flights. Status {response.status_code}"}]

                data = response.json()
                return self._format_duffel_offers(data.get("data", {}).get("offers", []))

        except Exception as e:
            print(f"ERROR: Duffel API connection failure: {e}")
            return [{"error": "Failed to connect to flight API"}]

    def _format_duffel_offers(self, raw_offers: list) -> List[Dict]:
        formatted_flights = []
        
        # Limit results to the top 3 items to optimize payload size
        for offer in raw_offers[:3]: 
            airline_name = offer["owner"]["name"]
            insights = self._get_custom_airline_insights(airline_name)

            formatted_flights.append({
                "flightId": offer["id"],
                "airline": airline_name,
                "priceEstimate": f"€{offer['total_amount']}",
                "insights": insights
            })
            
        return formatted_flights

    def _get_custom_airline_insights(self, airline: str) -> Dict:
        report_data = {
            "Ryanair": {
                "price": "Very low",
                "comfort": "Low, basic but acceptable for short flights",
                "service": "Generally friendly but limited service",
                "baggagePolicy": "Strict but clear rules",
                "reliability": "Often punctual"
            },
            "LOT Polish Airlines": {
                "price": "Low prices",
                "comfort": "Medium-low depends on the aircraft",
                "service": "Sometimes professional, sometimes unresponsive",
                "baggagePolicy": "Issues reported",
                "reliability": "Delays and cancellations reported"
            },
            "Wizz Air": {
                "price": "Low prices",
                "comfort": "Medium, newer aircraft but still basic",
                "service": "Inconsistent, often criticized",
                "baggagePolicy": "Strict and confusing",
                "reliability": "Unreliable, poor disruption handling"
            }
        }
        
        return report_data.get(airline, {
            "price": "Unknown",
            "comfort": "Unknown",
            "service": "Unknown",
            "baggagePolicy": "Check airline website",
            "reliability": "Unknown"
        })