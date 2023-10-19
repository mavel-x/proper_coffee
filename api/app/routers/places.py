from typing import Annotated

import httpx
from fastapi import Depends, HTTPException, status, APIRouter
from sqlmodel import Session, select

from app.dependencies import get_geocoder, SessionDropIn
from app.geocoding import Geocoder, GeocodingError
from app.models.places import (
    Location,
    LocationIn,
    Place,
    PlaceCreate,
    PlaceReadWithLocation,
    PlaceReadWithDistance,
)
from app.utils import haversine_distance
from app.database import get_or_create

router = APIRouter()

session_dep = Annotated[Session, Depends(SessionDropIn)]


@router.post("/places/")
def create_place(
        place: PlaceCreate,
        session: session_dep,
        geocoder: Annotated[Geocoder, Depends(get_geocoder)]
):
    try:
        location_in = LocationIn(**geocoder.geocode(place.address))
    except httpx.HTTPError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail='The geocoding service is currently unavailable. Please try again later.'
        )
    except GeocodingError as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=error.args[0])
    location_db = get_or_create(session, Location, **location_in.dict())
    place_db = Place(**place.dict(), location_id=location_db.id)
    session.add(place_db)
    session.commit()
    session.refresh(place_db)
    return place_db


@router.get("/places/{place_id}", response_model=PlaceReadWithLocation)
def get_place(
        place_id: int,
        session: session_dep,
):
    place = session.get(Place, place_id)
    if not place:
        raise HTTPException(status_code=404, detail="Place not found")
    return place


@router.post("/get-nearest/")
def get_nearest(user_location: LocationIn, session: session_dep):
    locations = session.exec(select(Location)).all()
    distances = {location.id: haversine_distance(user_location.latitude, user_location.longitude,
                                                 location.latitude, location.longitude)
                 for location in locations}
    nearest_loc_ids = sorted(distances, key=distances.get)[:3]
    statement = select(Place).where(Place.location_id.in_(nearest_loc_ids))
    nearest_places = session.exec(statement).all()
    nearest_places_with_distances = [
        PlaceReadWithDistance(**place.dict(), distance=distances[place.location_id], location=place.location.dict())
        for place in nearest_places
    ]
    return sorted(nearest_places_with_distances, key=lambda place: place.distance)
