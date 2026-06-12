from abc import ABC, abstractmethod
from typing import List, Optional
from pydantic import BaseModel
import math
import uuid

# ==========================================
# 1. SHARED DATA STRUCTURES
# ==========================================
class MedicalNode(BaseModel):
    id: str
    name: str
    facility_type: str
    lat: float
    lng: float
    is_24_7: bool
    local_phone: str
    emergency_dispatch: str

class Coordinate(BaseModel):
    lat: float
    lng: float

class Place(BaseModel):
    id: str
    name: str
    coords: Coordinate
    durationMins: int

class OptimizeRequest(BaseModel):
    days: int
    hotel: Place
    places: List[Place]
    class Config:
        json_schema_extra = {
            "example": {
                "days": 1,
                "hotel": {
                    "id": "hot_111",
                    "name": "Hotel Danieli",
                    "coords": {
                    "lat": 45.4337,
                    "lng": 12.3421
                    },
                    "durationMins": 0
                },
                "places": [
                    {
                    "id": "ChIJiYRBbtexfkcR0XTK3ATSCbg",
                    "name": "Doge's Palace",
                    "coords": {
                        "lat": 45.4337035,
                        "lng": 12.3403894
                    },
                    "durationMins": 45
                    },
                    {
                    "id": "10",
                    "name": "Forte di Sant'Andrea",
                    "coords": {
                        "lat": 45.4346,
                        "lng": 12.3811
                    },
                    "durationMins": 60
                    }
                ]
                }
        }

class RouteStep(BaseModel):
    step: int
    name: str
    coords: Coordinate
    isHotel: bool
    isSafetyNode: bool = False # <-- NEW: Flag for your frontend map icons!
    travelToNextMins: Optional[int] = None

class DailyRoute(BaseModel):
    dayNumber: int
    totalTimeMinutes: int
    route: List[RouteStep]

class OptimizeResponse(BaseModel):
    tripId: str
    dailyRoutes: List[DailyRoute]

# ==========================================
# 2. THE CONTRACT 
# ==========================================
class IRouteOptimizer(ABC):
    @abstractmethod
    # Notice this now expects List[MedicalNode] instead of List[Coordinate]
    def calculate_route(self, trip_duration_days: int, hotel: Place, places: List[Place], medical_nodes: List[MedicalNode]) -> OptimizeResponse:
        pass

# ==========================================
# 3. THE IMPLEMENTATION (Inline Injection)
# ==========================================
class SafeMedicalOptimizer(IRouteOptimizer):

    def _calculate_distance(self, coord1: Coordinate, coord2: Coordinate) -> float:
        return math.sqrt((coord1.lat - coord2.lat)**2 + (coord1.lng - coord2.lng)**2)
    


    def _calculate_travel_time(self, from_coords: Coordinate, to_coords: Coordinate) -> int:
      
        R = 6371  # Earth radius in km
    
        lat1 = math.radians(from_coords.lat)
        lat2 = math.radians(to_coords.lat)
        dlat = math.radians(to_coords.lat - from_coords.lat)
        dlng = math.radians(to_coords.lng - from_coords.lng)
    
        a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlng / 2) ** 2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
        distance_km = R * c
    
        walking_speed_kmh = 4.0
        time_minutes = (distance_km / walking_speed_kmh) * 60
    
        return max(1, round(time_minutes))  # minimum 1 dakika


    def _get_midpoint(self, coord1: Coordinate, coord2: Coordinate) -> Coordinate:
        return Coordinate(
            lat=(coord1.lat + coord2.lat) / 2,
            lng=(coord1.lng + coord2.lng) / 2
        )
        
    def _is_high_risk(self, coord: Coordinate, medical_nodes: List[MedicalNode]) -> bool:
        if not medical_nodes: 
            return False
        # Compare coordinate to the medical node's lat/lng
        shortest_dist = min([math.sqrt((coord.lat - n.lat)**2 + (coord.lng - n.lng)**2) for n in medical_nodes])
        return shortest_dist >= 0.025

    def calculate_route(self, trip_duration_days: int, hotel: Place, places: List[Place], medical_nodes: List[MedicalNode]) -> OptimizeResponse:
        places_per_day = max(1, len(places) // trip_duration_days)
        daily_clusters = [
           places[i:i + places_per_day]
           for i in range(0, len(places), places_per_day)
        ]
        final_routes = []
        
        for day_index, cluster in enumerate(daily_clusters):
            unvisited = cluster.copy()
            current_location = hotel.coords
            ordered_route = []
            
            # --- 1. MACRO-ROUTING (Find Order) ---
            while unvisited:
                best_place = None
                best_score = float('inf')
                for place in unvisited:
                    dist_to_place = self._calculate_distance(current_location, place.coords)
                    if dist_to_place < best_score:
                        best_score = dist_to_place
                    best_place = place
                ordered_route.append(best_place)
                current_location = best_place.coords
                unvisited.remove(best_place)

            # --- 2. MICRO-ROUTING (Inline Waypoint Injection) ---
            route_steps = []
            step_counter = 1 # We use a counter now so the step numbers stay sequential!
            
            route_steps.append(RouteStep(step=step_counter,
                                          name=hotel.name, 
                                          coords=hotel.coords,
                                          isHotel=True,
                                          travelToNextMins=15))
            step_counter += 1
            
            prev_location = hotel.coords
            for place in ordered_route:
                
                # Check for High Risk jump
                if self._is_high_risk(prev_location, medical_nodes) or self._is_high_risk(place.coords, medical_nodes):
                    if medical_nodes:
                        midpoint = self._get_midpoint(prev_location, place.coords)
                        
                        # Find closest hospital
                        closest_node = min(medical_nodes, key=lambda n: math.sqrt((midpoint.lat - n.lat)**2 + (midpoint.lng - n.lng)**2))
                        
                        dist_a_to_b = self._calculate_distance(prev_location, place.coords)
                        dist_a_to_node = math.sqrt((prev_location.lat - closest_node.lat)**2 + (prev_location.lng - closest_node.lng)**2)
                        dist_node_to_b = math.sqrt((closest_node.lat - place.coords.lat)**2 + (closest_node.lng - place.coords.lng)**2)
                        
                        # Sanity check
                        if dist_a_to_node <= dist_a_to_b and dist_node_to_b <= dist_a_to_b:
                            
                            # ---> INJECT HOSPITAL AS A FULL ROUTE STEP! <---
                            route_steps.append(RouteStep(
                                step=step_counter, 
                                name=f"Safety Checkpoint: {closest_node.name}", 
                                coords=Coordinate(lat=closest_node.lat, lng=closest_node.lng), 
                                isHotel=False, 
                                isSafetyNode=True, 
                                travelToNextMins=self._calculate_travel_time(
                                     prev_location, 
                                      Coordinate(lat=closest_node.lat, lng=closest_node.lng)
                                )
                            ))
                            step_counter += 1
                            prev_location = Coordinate(lat=closest_node.lat, lng=closest_node.lng) 

                # Add the actual tourist destination
                travel_mins = self._calculate_travel_time(prev_location, place.coords)
                route_steps.append(RouteStep(
                    step=step_counter, 
                    name=place.name, 
                    coords=place.coords, 
                    isHotel=False, 
                    travelToNextMins=travel_mins
                ))
                step_counter += 1
                prev_location = place.coords
                
            route_steps.append(RouteStep(step=step_counter, name=hotel.name, coords=hotel.coords, isHotel=True))
            
            final_routes.append(DailyRoute(dayNumber=day_index + 1, totalTimeMinutes=320, route=route_steps))

        return OptimizeResponse(tripId=str(uuid.uuid4()), dailyRoutes=final_routes)