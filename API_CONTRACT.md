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

## 3. Get Trip Cheat Sheet
Fetches local rules and nuances for the requested city.
* **URL:** `/api/nuances?city=Warsaw`
* **Method:** `GET`

**Response Body:**
```json
{
  "city": "Warsaw",
  "cheatSheet": [
    { "category": "Transport", "tip": "Validate paper tickets upon boarding." },
    { "category": "Dining", "tip": "Tipping 10% is standard in sit-down restaurants." }
  ]
}
```