from typing import Annotated

from fastapi import APIRouter, Depends, status
from geopy.distance import geodesic

from app.api.dependencies import get_coffee_repo, get_geocoding_service
from app.core.schemas import (
    CreatedResponse,
    Location,
    Place,
    PlaceCreate,
    PlaceWithDistance,
)
from app.services.geocoding import GeocodingService
from app.services.place.repository import PlaceRepository

v1_router = APIRouter(prefix="/coffee", tags=["coffee"])


@v1_router.post(
    "/create",
    status_code=status.HTTP_201_CREATED,
    response_description="Created",
    response_model=CreatedResponse,
    responses={
        status.HTTP_400_BAD_REQUEST: {
            "content": {
                "application/json": {
                    "example": {"detail": "Unable to geocode address: <address>"},
                },
            },
        },
        status.HTTP_409_CONFLICT: {
            "content": {
                "application/json": {
                    "example": {"detail": "Location already exists"},
                },
            },
        },
    },
)
async def create_place(
    geocoding_service: Annotated[GeocodingService, Depends(get_geocoding_service)],
    coffee_repo: Annotated[PlaceRepository, Depends(get_coffee_repo)],
    place_create: PlaceCreate,
):
    location = await geocoding_service.geocode(place_create.address)
    place_with_location = Place.model_validate(place_create.model_dump() | {"location": location})
    created_id = await coffee_repo.add_one(place_with_location)
    return {"id": created_id}


@v1_router.get("/nearest", response_model=list[PlaceWithDistance])
async def get_nearest(
    coffee_repo: Annotated[PlaceRepository, Depends(get_coffee_repo)],
    latitude: float,
    longitude: float,
):
    user_location = Location(latitude=latitude, longitude=longitude)
    nearest_places = await coffee_repo.get_nearest(user_location)

    places_with_distance = []
    for place in nearest_places:
        distance_km = geodesic(user_location.to_point(), place.location.to_point()).km
        places_with_distance.append(PlaceWithDistance.model_validate(place.model_dump() | {"distance_km": distance_km}))

    return sorted(places_with_distance, key=lambda p: p.distance_km)


@v1_router.get(
    "/{place_id}",
    response_model=Place,
    responses={
        status.HTTP_404_NOT_FOUND: {
            "content": {
                "application/json": {
                    "example": {"detail": "Place with id <id> not found"},
                },
            },
        },
    },
)
async def get_place(
    coffee_repo: Annotated[PlaceRepository, Depends(get_coffee_repo)],
    place_id: int,
):
    return await coffee_repo.get_by_id(place_id)
