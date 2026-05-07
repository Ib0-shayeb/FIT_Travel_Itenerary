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

        # 1. Dynamically build the passenger list
        passengers = []
        for _ in range(adults):
            passengers.append({"type": "adult"})
        for _ in range(children):
            # Duffel requires an exact age for minors, but you CANNOT send the "type" key
            passengers.append({"age": 10})

        # 2. Build the dynamic Duffel Offer Request Payload
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

        print(f"📡 Sending Request to Duffel: {origin_code.upper()} -> {destination_code.upper()} on {departure_date} ({adults} Adults, {children} Kids)...")

        # 3. Make the API Call
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/offer_requests",
                    headers=self.headers,
                    json=payload,
                    timeout=10.0
                )
                
                if response.status_code != 201 and response.status_code != 200:
                    print(f"❌ Duffel API Error: {response.text}")
                    return [{"error": f"Failed to fetch flights. Status {response.status_code}"}]

                data = response.json()
                return self._format_duffel_offers(data.get("data", {}).get("offers", []))

        except Exception as e:
            print(f"❌ Network Error: {e}")
            return [{"error": "Failed to connect to flight API"}]

    def _format_duffel_offers(self, raw_offers: list) -> List[Dict]:
        formatted_flights = []
        
        # Just grab the top 3 cheapest flights so we don't overwhelm the frontend
        for offer in raw_offers[:3]: 
            # Extract the airline name from the complex Duffel JSON structure
            airline_name = offer["owner"]["name"]
            
            # Use our custom report data to inject insights!
            insights = self._get_custom_airline_insights(airline_name)

            formatted_flights.append({
                "flightId": offer["id"],
                "airline": airline_name,
                "priceEstimate": f"€{offer['total_amount']}",
                "insights": insights
            })
            
        return formatted_flights

    def _get_custom_airline_insights(self, airline: str) -> Dict:
        """
        This matches the exact Review Analysis from your university report!
        (Note: Duffel Test environment usually returns 'Duffel Airways', 
        so we added a fallback for that).
        """
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
        
        # If the airline is in our report, use our custom data. 
        # Otherwise, return a generic safe response.
        return report_data.get(airline, {
            "price": "Unknown",
            "comfort": "Unknown",
            "service": "Unknown",
            "baggagePolicy": "Check airline website",
            "reliability": "Unknown"
        })