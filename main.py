from pathlib import Path

import requests.exceptions
from fastapi import FastAPI, Depends, HTTPException, status
from sqlmodel import Session, SQLModel, create_engine, select

from models import (
    Place,
    PlaceCreate,
    Location,
    LocationIn,
    PlaceReadWithLocation,
    PlaceReadWithDistance,
)
from settings import Settings
from utils import get_or_create, haversine_distance
from exceptions import GeocodingError


DATABASE_PATH = Path('./test.sqlite3')
DATABASE_URL = f'sqlite:///{DATABASE_PATH}'
engine = None

settings = Settings()
app = FastAPI()


@app.on_event("startup")
def on_startup():
    global engine
    engine = create_engine(DATABASE_URL)
    SQLModel.metadata.create_all(engine)


def get_db_session():
    with Session(engine) as session:
        yield session


@app.post("/places/")
def create_place(place: PlaceCreate, session: Session = Depends(get_db_session)):
    try:
        location_in = LocationIn.from_address(place.address, settings.geo_api)
    except requests.exceptions.HTTPError as error:
        raise HTTPException(status_code=error.response.status_code, detail=error.args[0])
    except GeocodingError as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=error.args[0])
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
