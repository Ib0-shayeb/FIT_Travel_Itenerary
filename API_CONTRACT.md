# Trip Planner API Contract

## 1. Optimize Trip Route
Calculates the optimal daily schedule based on selected places using K-Means clustering and TSP.
* **URL:** `/api/trips/optimize`
* **Method:** `POST`

**Request Body (Frontend -> Backend):**
```json
{
  "tripDurationDays": 3,
  "hotelStartingPoint": {
    "placeId": "hotel_123",
    "name": "Marriott Warsaw",
    "lat": 52.2285, "lng": 21.0034
  },
  "selectedPlaces": [
    {
      "placeId": "museum_456",
      "name": "National Museum",
      "lat": 52.2317, "lng": 21.0245,
      "durationMinutes": 90 
    },
    {
      "placeId": "park_789",
      "name": "Lazienki Park",
      "lat": 52.2150, "lng": 21.0353,
      "durationMinutes": 120 
    }
  ]
}
```

**Response Body (Backend -> Frontend):**
```json
{
  "tripId": "trip_98765",
  "dailyRoutes": [
    {
      "dayNumber": 1,
      "totalTimeMinutes": 320,
      "route": [
        { "step": 1, "name": "Marriott Warsaw", "isHotel": true },
        { "step": 2, "name": "National Museum", "travelToNextMins": 15 },
        { "step": 3, "name": "Lazienki Park", "travelToNextMins": 20 },
        { "step": 4, "name": "Marriott Warsaw", "isHotel": true }
      ]
    }
  ]
}
```

---

## 2. Get Places (Explore Page)
Fetches popular spots and hidden gems for a specific city.
* **URL:** `/api/places?city=Warsaw`
* **Method:** `GET`

**Response Body:**
```json
{
  "city": "Warsaw",
  "places": [
    {
      "placeId": "castle_111",
      "name": "Royal Castle",
      "category": "Popular",
      "lat": 52.2479, "lng": 21.0142
    },
    {
      "placeId": "gem_222",
      "name": "Neon Museum",
      "category": "Hidden Gem",
      "lat": 52.2486, "lng": 21.0478
    }
  ]
}
```

---

## 3. Get Trip Cheat Sheet (Nuances)
Fetches specific local rules and nuances based on the exact places the user plans to visit.
* **URL:** `/api/nuances`
* **Method:** `POST`

**Request Body (Frontend -> Backend):**
```json
{
  "selectedPlaces": [
    {
      "placeId": "v_pop_1",
      "name": "Schönbrunn Palace",
      "category": "Popular"
    },
    {
      "placeId": "v_gem_1",
      "name": "Hundertwasserhaus",
      "category": "Hidden Gem"
    }
  ]
}
```

**Response Body (Backend -> Frontend):**
```json
{
  "cheatSheet": [
    { 
      "category": "Attraction Specific", 
      "tip": "Photography is strictly prohibited inside the main state rooms of Schönbrunn Palace." 
    },
    { 
      "category": "Transport", 
      "tip": "Take the U4 subway line directly to the Schönbrunn station." 
    },
    { 
      "category": "Neighborhood", 
      "tip": "The area around Hundertwasserhaus is residential; please keep noise levels down." 
    }
  ]
}
```

## 4. Get Place Recommendations
Returns a mix of Google API popular spots and hard-coded hidden gems.
* **URL:** `/api/recommendations/places`
* **Method:** `GET`

**Response Body:**
```json
{
  "city": "Vienna",
  "places": [
    {
      "placeId": "v_pop_1",
      "name": "Schönbrunn Palace",
      "category": "Popular",
      "rating": 4.8,
      "reviewVolume": 45000,
      "lat": 48.1848,
      "lng": 16.3122
    },
    {
      "placeId": "v_gem_1",
      "name": "Hundertwasserhaus",
      "category": "Hidden Gem",
      "rating": 4.6,
      "reviewVolume": 1200,
      "lat": 48.2077,
      "lng": 16.3939
    }
  ]
}
```

---

## 5. Get Flight Recommendations
Returns flight options combined with our custom Airline Review Analysis.
* **URL:** `/api/recommendations/flights`
* **Method:** `GET`

**Response Body:**
```json
{
  "destination": "Vienna",
  "flights": [
    {
      "flightId": "FR1234",
      "airline": "Ryanair",
      "priceEstimate": "€45",
      "insights": {
        "price": "Very low",
        "comfort": "Low, basic but acceptable for short flights",
        "service": "Generally friendly but limited service",
        "baggagePolicy": "Strict but clear rules",
        "reliability": "Often punctual"
      }
    },
    {
      "flightId": "W65432",
      "airline": "Wizz Air",
      "priceEstimate": "€38",
      "insights": {
        "price": "Low prices",
        "comfort": "Medium, newer aircraft but still basic",
        "service": "Inconsistent, often criticized",
        "baggagePolicy": "Strict and confusing",
        "reliability": "Unreliable, poor disruption handling"
      }
    }
  ]
}
```

---

## 6. Get Hotel Recommendations
Returns accommodations centered around the route, filtered by safety and providing external booking links.
* **URL:** `/api/recommendations/hotels`
* **Method:** `GET`

**Response Body:**
```json
{
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
      "externalBookingLink": "[https://www.booking.com/hotel/at/motel-one-wien-staatsoper.html](https://www.booking.com/hotel/at/motel-one-wien-staatsoper.html)"
    }
  ]
}
```