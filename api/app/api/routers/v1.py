from typing import Annotated

from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse

from app.api.dependencies import get_coffee_repo, get_geocoding_service
from app.core.schemas import Location, Place, PlaceCreate, PlaceCreatedResponse, PlaceWithDistance
from app.services.geocoding import GeocodingService
from app.services.place.repository import PlaceRepository

v1_router = APIRouter(prefix="/coffee", tags=["coffee"])


@v1_router.post(
    "/create",
    status_code=status.HTTP_201_CREATED,
    response_model=PlaceCreatedResponse,
)
async def create_place(
    place_create: PlaceCreate,
    geocoding_service: Annotated[GeocodingService, Depends(get_geocoding_service)],
    coffee_repo: Annotated[PlaceRepository, Depends(get_coffee_repo)],
):
    location = await geocoding_service.geocode(place_create.address)
    place_with_location = Place.model_validate(place_create.model_dump() | {"location": location})
    created_id = await coffee_repo.add_one(place_with_location)
    return JSONResponse(status_code=status.HTTP_201_CREATED, content={"id": created_id})


@v1_router.get("/{place_id}", response_model=Place)
async def get_place(place_id: int, place_repo: Annotated[PlaceRepository, Depends(get_coffee_repo)]):
    return await place_repo.get_by_id(place_id)


@v1_router.post("/nearest", response_model=list[PlaceWithDistance])
async def get_nearest(user_location: Location, place_repo: Annotated[PlaceRepository, Depends(get_coffee_repo)]):
    nearest_places = await place_repo.get_nearest(user_location)
    return sorted(nearest_places, key=lambda place: place.distance_km)
