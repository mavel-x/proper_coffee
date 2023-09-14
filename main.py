from pathlib import Path

from fastapi import FastAPI, Depends, HTTPException
from sqlmodel import Session, SQLModel, create_engine

from models import Place, PlaceCreate, Location, LocationIn
from settings import Settings
from utils import get_or_create, haversine_distance


DATABASE_PATH = Path('./test.sqlite3')
DATABASE_URL = f'sqlite:///{DATABASE_PATH}'
engine = create_engine(DATABASE_URL)

settings = Settings()
app = FastAPI()


@app.on_event("startup")
def on_startup():
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


@app.post("/get-nearest/")
def get_nearest(user_location: LocationIn, session: Session = Depends(get_db_session)):
    return user_location
