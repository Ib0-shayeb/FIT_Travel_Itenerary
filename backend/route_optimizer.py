from abc import ABC, abstractmethod
from typing import List, Optional
from pydantic import BaseModel
import math
import uuid


# ==========================================
# 1. SHARED DATA STRUCTURES
# ==========================================

class Coordinate(BaseModel):
    lat: float
    lng: float


class Place(BaseModel):
    id: str
    name: str
    lat: float
    lng: float


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
# 2. CONTRACT
# ==========================================

class IRouteOptimizer(ABC):

    @abstractmethod
    def calculate_route(
        self,
        trip_duration_days: int,
        hotel: Place,
        places: List[Place],
        medical_nodes: List[Coordinate]
    ) -> OptimizeResponse:
        pass


# ==========================================
# 3. IMPLEMENTATION
# ==========================================

class SafeMedicalOptimizer(IRouteOptimizer):

    def _calculate_distance(
        self,
        coord1: Coordinate,
        coord2: Coordinate
    ) -> float:

        return math.sqrt(
            (coord1.lat - coord2.lat) ** 2 +
            (coord1.lng - coord2.lng) ** 2
        )

    def calculate_route(
        self,
        trip_duration_days: int,
        hotel: Place,
        places: List[Place],
        medical_nodes: List[Coordinate]
    ) -> OptimizeResponse:

        daily_clusters = [places]
        final_routes = []

        for day_index, cluster in enumerate(daily_clusters):

            unvisited = cluster.copy()

            current_location = Coordinate(
                lat=hotel.lat,
                lng=hotel.lng
            )

            ordered_route = []

            while unvisited:

                best_place = None
                best_score = float("inf")

                for place in unvisited:

                    place_coord = Coordinate(
                        lat=place.lat,
                        lng=place.lng
                    )

                    dist_to_place = self._calculate_distance(
                        current_location,
                        place_coord
                    )

                    if medical_nodes:
                        min_hospital_dist = min(
                            self._calculate_distance(place_coord, m)
                            for m in medical_nodes
                        )
                    else:
                        min_hospital_dist = 0

                    penalty = 1.0

                    if min_hospital_dist > 0.02:
                        penalty = 5.0

                    score = dist_to_place * penalty

                    if score < best_score:
                        best_score = score
                        best_place = place

                if best_place is None:
                    break

                ordered_route.append(best_place)

                current_location = Coordinate(
                    lat=best_place.lat,
                    lng=best_place.lng
                )

                unvisited.remove(best_place)

            route_steps = []

            # Start Hotel
            route_steps.append(
                RouteStep(
                    step=1,
                    name=hotel.name,
                    coords=Coordinate(
                        lat=hotel.lat,
                        lng=hotel.lng
                    ),
                    isHotel=True,
                    travelToNextMins=15
                )
            )

            # Places
            for i, place in enumerate(ordered_route):

                place_coord = Coordinate(
                    lat=place.lat,
                    lng=place.lng
                )

                if medical_nodes:
                    dist_to_hosp = min(
                        self._calculate_distance(place_coord, m)
                        for m in medical_nodes
                    )
                else:
                    dist_to_hosp = 0

                mock_meters = int(dist_to_hosp * 100000)

                route_steps.append(
                    RouteStep(
                        step=i + 2,
                        name=place.name,
                        coords=place_coord,
                        isHotel=False,
                        travelToNextMins=10,
                        distanceToHospitalMeter=mock_meters
                    )
                )

            # Return Hotel
            route_steps.append(
                RouteStep(
                    step=len(ordered_route) + 2,
                    name=hotel.name,
                    coords=Coordinate(
                        lat=hotel.lat,
                        lng=hotel.lng
                    ),
                    isHotel=True
                )
            )

            final_routes.append(
                DailyRoute(
                    dayNumber=day_index + 1,
                    totalTimeMinutes=320,
                    route=route_steps
                )
            )

        return OptimizeResponse(
            tripId=str(uuid.uuid4()),
            dailyRoutes=final_routes
        )