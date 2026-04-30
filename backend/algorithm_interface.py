from abc import ABC, abstractmethod
from typing import List, Optional
from pydantic import BaseModel

# ==========================================
# 1. INPUT DATA STRUCTURES (What you give the algorithm)
# ==========================================

class LocationInput(BaseModel):
    placeId: str
    name: str
    lat: float
    lng: float
    durationMinutes: int = 0  # Time spent at the location

class HotelInput(BaseModel):
    placeId: str
    name: str
    lat: float
    lng: float

# ==========================================
# 2. OUTPUT DATA STRUCTURES (What the algorithm gives back)
# ==========================================

class RouteStep(BaseModel):
    stepOrder: int
    name: str
    isHotel: bool = False
    travelToNextMins: int = 0

class DailyRoute(BaseModel):
    dayNumber: int
    totalTimeMinutes: int
    route: List[RouteStep]

class OptimizedRouteResult(BaseModel):
    tripId: str
    dailyRoutes: List[DailyRoute]

# ==========================================
# 3. THE CONTRACT (The Interface)
# ==========================================

class IRouteOptimizer(ABC):
    """
    Any class that implements this interface MUST provide a functioning 
    calculate_route method that takes these exact inputs and returns this exact output.
    """
    
    @abstractmethod
    def calculate_route(self, 
                        trip_duration_days: int, 
                        hotel: HotelInput, 
                        places: List[LocationInput]) -> OptimizedRouteResult:
        pass