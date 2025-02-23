from typing import Annotated

from fastapi import APIRouter, Depends, status
from shapely.geometry.point import Point

from app.api.dependencies import get_coffee_repo, get_geocoding_service
from app.core.schemas import (
    CreatedResponse,
    Place,
    PlaceCreate,
    PlaceCreateGeocoded,
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
    place_create: PlaceCreate,
    geocoding_service: Annotated[GeocodingService, Depends(get_geocoding_service)],
    coffee_repo: Annotated[PlaceRepository, Depends(get_coffee_repo)],
):
    location = await geocoding_service.geocode(place_create.address)
    place_with_location = PlaceCreateGeocoded.model_validate(place_create.model_dump() | {"location": location})
    created_id = await coffee_repo.add_one(place_with_location)
    return {"id": created_id}


@v1_router.get("/nearest", response_model=list[Place])
async def get_nearest(
    latitude: float,
    longitude: float,
    place_repo: Annotated[PlaceRepository, Depends(get_coffee_repo)],
):
    location_point = Point(longitude, latitude)
    nearest_places = await place_repo.get_nearest(location_point)
    return nearest_places
    # return sorted(nearest_places, key=lambda place: place.distance_km)


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
async def get_place(place_id: int, place_repo: Annotated[PlaceRepository, Depends(get_coffee_repo)]):
    return await place_repo.get_by_id(place_id)
