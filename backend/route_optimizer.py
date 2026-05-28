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
                    "coords": {"lat": 45.4337, "lng": 12.3421},
                    "durationMins": 0
                },
                "places": [
                    {
                        "id": "pl_1",
                        "name": "St. Mark's Basilica",
                        "coords": {"lat": 45.4346, "lng": 12.3397},
                        "durationMins": 60
                    },
                    {
                        "id": "pl_2",
                        "name": "Rialto Bridge",
                        "coords": {"lat": 45.4381, "lng": 12.3358},
                        "durationMins": 45
                    }
                ]
            }
        }

class RouteStep(BaseModel):
    step: int
    name: str
    coords: Coordinate
    isHotel: bool
    travelToNextMins: Optional[int] = None
    # NEW: The Micro-Routing Safety Waypoints!
    safetyWaypoints: Optional[List[Coordinate]] = [] 

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
    def calculate_route(self, trip_duration_days: int, hotel: Place, places: List[Place], medical_nodes: List[Coordinate]) -> OptimizeResponse:
        pass

# ==========================================
# 3. THE IMPLEMENTATION (Waypoint Injection)
# ==========================================
class SafeMedicalOptimizer(IRouteOptimizer):

    def _calculate_distance(self, coord1: Coordinate, coord2: Coordinate) -> float:
        return math.sqrt((coord1.lat - coord2.lat)**2 + (coord1.lng - coord2.lng)**2)

    def _get_midpoint(self, coord1: Coordinate, coord2: Coordinate) -> Coordinate:
        return Coordinate(
            lat=(coord1.lat + coord2.lat) / 2,
            lng=(coord1.lng + coord2.lng) / 2
        )
        
    def _is_high_risk(self, coord: Coordinate, medical_nodes: List[Coordinate]) -> bool:
        if not medical_nodes: 
            return False
        # Matches the 0.025 threshold from your places_client.py
        shortest_dist = min([self._calculate_distance(coord, m) for m in medical_nodes])
        return shortest_dist >= 0.025

    def calculate_route(self, trip_duration_days: int, hotel: Place, places: List[Place], medical_nodes: List[Coordinate]) -> OptimizeResponse:
        daily_clusters = [places] 
        final_routes = []
        
        for day_index, cluster in enumerate(daily_clusters):
            unvisited = cluster.copy()
            current_location = hotel.coords
            ordered_route = []
            
            # --- 1. MACRO-ROUTING (Pure Shortest Path) ---
            while unvisited:
                best_place = None
                best_score = float('inf')
                
                for place in unvisited:
                    # No more hidden penalties. Just find the closest logical next stop!
                    dist_to_place = self._calculate_distance(current_location, place.coords)
                    
                    if dist_to_place < best_score:
                        best_score = dist_to_place
                        best_place = place
                        
                ordered_route.append(best_place)
                current_location = best_place.coords
                unvisited.remove(best_place)

            # --- 2. MICRO-ROUTING (Waypoint Injection) ---
            route_steps = []
            route_steps.append(RouteStep(step=1, name=hotel.name, coords=hotel.coords, isHotel=True, travelToNextMins=15))
            
            prev_location = hotel.coords
            for i, place in enumerate(ordered_route):
                
                waypoints = []
                
                # Check if either Point A (prev) or Point B (curr) is High Risk
                if self._is_high_risk(prev_location, medical_nodes) or self._is_high_risk(place.coords, medical_nodes):
                    if medical_nodes:
                        midpoint = self._get_midpoint(prev_location, place.coords)
                        
                        # Find the absolute closest hospital to the midpoint
                        closest_node = min(medical_nodes, key=lambda n: self._calculate_distance(midpoint, n))
                        
                        # Your brilliant Sanity Check Math:
                        dist_a_to_b = self._calculate_distance(prev_location, place.coords)
                        dist_a_to_node = self._calculate_distance(prev_location, closest_node)
                        dist_node_to_b = self._calculate_distance(closest_node, place.coords)
                        
                        # Only inject it if it doesn't force them to walk away from their destination!
                        if dist_a_to_node <= dist_a_to_b and dist_node_to_b <= dist_a_to_b:
                            waypoints.append(closest_node)

                route_steps.append(RouteStep(
                    step=i + 2, 
                    name=place.name, 
                    coords=place.coords, 
                    isHotel=False, 
                    travelToNextMins=10, 
                    safetyWaypoints=waypoints # Injected!
                ))
                prev_location = place.coords
                
            route_steps.append(RouteStep(step=len(ordered_route) + 2, name=hotel.name, coords=hotel.coords, isHotel=True))
            
            final_routes.append(DailyRoute(dayNumber=day_index + 1, totalTimeMinutes=320, route=route_steps))

        return OptimizeResponse(tripId=str(uuid.uuid4()), dailyRoutes=final_routes)