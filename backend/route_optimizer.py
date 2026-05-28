from abc import ABC, abstractmethod
from typing import List, Optional
from pydantic import BaseModel
import math
import uuid

# ==========================================
# 1. SHARED DATA STRUCTURES
# (These perfectly match what main.py expects)
# ==========================================

class Coordinate(BaseModel):
    lat: float
    lng: float

class Place(BaseModel):
    id: str
    name: str
    coords: Coordinate
    durationMins: int

class MedicalNode(BaseModel):
    id: str
    name: str
    facility_type: str
    lat: float
    lng: float
    is_24_7: bool
    local_phone: str
    emergency_dispatch: str

class OptimizeRequest(BaseModel):
    days: int
    hotel: Place
    places: List[Place]

class RouteStep(BaseModel):
    step: int
    name: str
    coords: Coordinate
    isHotel: bool
    travelToNextMins: Optional[int] = None
    distanceToHospitalMeter: Optional[int] = None

class DailyRoute(BaseModel):
    dayNumber: int
    totalTimeMinutes: int
    route: List[RouteStep]

class OptimizeResponse(BaseModel):
    tripId: str
    dailyRoutes: List[DailyRoute]

# ==========================================
# 2. THE CONTRACT (The Interface)
# ==========================================

class IRouteOptimizer(ABC):
    """
    Any class that implements this interface MUST provide a calculate_route 
    method. Notice we added `medical_nodes` to the required inputs!
    """
    
    @abstractmethod
    def calculate_route(self, 
                        trip_duration_days: int, 
                        hotel: Place, 
                        places: List[Place],
                        medical_nodes: List[Coordinate]) -> OptimizeResponse:
        pass

# ==========================================
# 3. THE IMPLEMENTATION (Safe Route Math)
# ==========================================

class SafeMedicalOptimizer(IRouteOptimizer):
    """
    This specific optimizer builds routes that prioritize keeping the 
    user within a safe distance of hospitals/medical nodes.
    """

    def _calculate_distance(self, coord1: Coordinate, coord2: Coordinate) -> float:
        # Internal helper function for math
        return math.sqrt((coord1.lat - coord2.lat)**2 + (coord1.lng - coord2.lng)**2)

    def calculate_route(self, trip_duration_days: int, hotel: Place, places: List[Place], medical_nodes: List[Coordinate]) -> OptimizeResponse:
        # 1. Mocking the K-Means Cluster (putting all places in day 1 for now)
        daily_clusters = [places] 
        final_routes = []
        
        for day_index, cluster in enumerate(daily_clusters):
            # --- START TSP SAFETY MATH ---
            unvisited = cluster.copy()
            current_location = hotel.coords
            ordered_route = []
            
            while unvisited:
                best_place = None
                best_score = float('inf')
                
                for place in unvisited:
                    dist_to_place = self._calculate_distance(current_location, place.coords)
                    min_hospital_dist = min([self._calculate_distance(place.coords, m) for m in medical_nodes])
                    
                    # The Safety Penalty!
                    penalty = 1.0
                    if min_hospital_dist > 0.02: 
                        penalty = 5.0 
                        
                    score = dist_to_place * penalty
                    
                    if score < best_score:
                        best_score = score
                        best_place = place
                        
                ordered_route.append(best_place)
                current_location = best_place.coords
                unvisited.remove(best_place)
            # --- END TSP SAFETY MATH ---

            # 2. Format the route for the response
            route_steps = []
            
            # Start at hotel
            route_steps.append(RouteStep(
                step=1, name=hotel.name, coords=hotel.coords, isHotel=True, travelToNextMins=15 
            ))
            
            # Add safely ordered places
            for i, place in enumerate(ordered_route):
                dist_to_hosp = min([self._calculate_distance(place.coords, m) for m in medical_nodes])
                mock_meters = int(dist_to_hosp * 100000) 

                route_steps.append(RouteStep(
                    step=i + 2, name=place.name, coords=place.coords, isHotel=False, travelToNextMins=10, distanceToHospitalMeter=mock_meters 
                ))
                
            # End at hotel
            route_steps.append(RouteStep(
                step=len(ordered_route) + 2, name=hotel.name, coords=hotel.coords, isHotel=True
            ))
            
            final_routes.append(DailyRoute(
                dayNumber=day_index + 1, totalTimeMinutes=320, route=route_steps
            ))

        return OptimizeResponse(
            tripId=str(uuid.uuid4()),
            dailyRoutes=final_routes
        )