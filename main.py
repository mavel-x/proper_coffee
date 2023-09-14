from pathlib import Path

from fastapi import FastAPI, Depends, HTTPException
from sqlmodel import Session, SQLModel, create_engine, select

from models import (
    Place,
    PlaceCreate,
    Location,
    LocationIn,
    LocationReadWithDistance,
    PlaceReadWithLocation,
    PlaceReadWithDistance,
)
from settings import Settings
from utils import get_or_create, haversine_distance


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
    location_in = LocationIn.from_address(place.address, settings.geo_api)
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
    distances = [haversine_distance(user_location.latitude, user_location.longitude,
                                    loc.latitude, loc.longitude)
                 for loc in locations]
    locations_with_distances = [LocationReadWithDistance(**loc.dict(), distance=dist)
                                for loc, dist in zip(locations, distances)]
    nearest_locations = sorted(
        locations_with_distances,
        key=lambda loc: loc.distance,
    )[:3]
    nearest_loc_ids = [loc.id for loc in nearest_locations]
    statement = select(Place).where(Place.location_id.in_(nearest_loc_ids))
    nearest_places = session.exec(statement).all()
    nearest_places_with_distances = [PlaceReadWithDistance(**place.dict(), distance=location.distance)
                                     for place, location
                                     in zip(sorted(nearest_places, key=lambda place: place.id),
                                            sorted(nearest_locations, key=lambda loc: loc.id))]
    return nearest_places_with_distances
