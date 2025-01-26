from typing import Annotated

import httpx
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.dependencies import SessionDropIn, get_geocoder
from app.repositories import LocationRepository, PlaceRepository
from app.schemas.location import Location
from app.schemas.place import Place, PlaceDBCreate, PlaceWithDistance, PlaceWithLocation
from app.services.geocoding import Geocoder, GeocodingError
from app.utils import haversine_distance

router = APIRouter()

session_dep = Annotated[Session, Depends(SessionDropIn)]


@router.post("/places/", response_model=PlaceWithLocation)
def create_place(
    place: Place,
    session: session_dep,
    geocoder: Annotated[Geocoder, Depends(get_geocoder)],
):
    try:
        location = geocoder.geocode(place.address)
    except httpx.HTTPError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="The geocoding service is currently unavailable. Please try again later.",
        ) from exc
    except GeocodingError as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=error.args[0]) from error
    location_db = LocationRepository(session).get_or_create(location)
    place_create = PlaceDBCreate(**place.model_dump(), location=location_db)
    PlaceRepository(session).add_one(place_create)
    session.commit()
    return place_create


@router.get("/places/{place_id}", response_model=PlaceWithLocation)
def get_place(
    place_id: int,
    session: session_dep,
):
    place = PlaceRepository(session).get_by_id(pk=place_id)
    if not place:
        raise HTTPException(status_code=404, detail="Place not found")
    return place


@router.post("/get-nearest/", response_model=list[PlaceWithDistance])
def get_nearest(
    user_location: Location,
    session: session_dep,
):
    locations = LocationRepository(session).get_all()
    distances = {
        location.id: haversine_distance(
            user_location.latitude, user_location.longitude, location.latitude, location.longitude
        )
        for location in locations
    }
    nearest_loc_ids = sorted(distances, key=distances.get)[:3]
    nearest_places = PlaceRepository(session).filter_in("location_id", nearest_loc_ids)
    nearest_places_with_distances = [
        PlaceWithDistance(
            **place.model_dump(),
            distance=distances[place.location.id],
        )
        for place in nearest_places
    ]
    return sorted(nearest_places_with_distances, key=lambda place: place.distance)
