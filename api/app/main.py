from pathlib import Path

import requests.exceptions
from fastapi import FastAPI, Depends, HTTPException, status
from sqlmodel import Session, SQLModel, create_engine, select

from app.geocoding import Geocoder, GeocodingError
from app.models import (
    Location,
    LocationIn,
    Place,
    PlaceCreate,
    PlaceReadWithLocation,
    PlaceReadWithDistance,
)
from app.settings import Settings
from app.utils import get_or_create, haversine_distance


BASE_DIR = Path(__file__).parent.parent
DATABASE_PATH = BASE_DIR / 'test.sqlite3'
DATABASE_URL = f'sqlite:///{DATABASE_PATH}'

settings = Settings()
app = FastAPI()


@app.on_event("startup")
def on_startup():
    app.state.geocoder = Geocoder(api_key=settings.geo_api)
    app.state.engine = create_engine(DATABASE_URL)
    SQLModel.metadata.create_all(app.state.engine)


def get_db_session():
    with Session(app.state.engine) as session:
        yield session


@app.post("/places/")
def create_place(place: PlaceCreate, session: Session = Depends(get_db_session)):
    geocoder = app.state.geocoder
    try:
        location_in = LocationIn(**geocoder.geocode(place.address))
    except requests.exceptions.HTTPError as error:
        raise HTTPException(status_code=error.response.status_code, detail=error.args[0])
    except GeocodingError as error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error.args[0])
    location_db = get_or_create(session, Location, **location_in.dict())
    place_db = Place(**place.dict(), location_id=location_db.id)
    session.add(place_db)
    session.commit()
    session.refresh(place_db)
    return place_db


@app.get("/places/{place_id}", response_model=PlaceReadWithLocation)
def get_place(place_id: int, session: Session = Depends(get_db_session)):
    place = session.get(Place, place_id)
    if not place:
        raise HTTPException(status_code=404, detail="Place not found")
    return place


@app.post("/get-nearest/")
def get_nearest(user_location: LocationIn, session: Session = Depends(get_db_session)):
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
    return nearest_places_with_distances
