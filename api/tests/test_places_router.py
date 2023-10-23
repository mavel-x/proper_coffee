import pytest
from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import Session
from sqlalchemy import create_engine

from app.dependencies import SessionDropIn
from app.models import Base
from app.main import app
from app.repositories import LocationRepository, PlaceRepository
from app.schemata.location import Location, LocationDB
from app.schemata.place import PlaceDBCreate


def load_test_data(session: Session):
    location_repo = LocationRepository(session)
    place_repo = PlaceRepository(session)
    location1 = Location(latitude=52.547250, longitude=13.358090)
    location2 = Location(latitude=52.543880, longitude=13.367920)
    location3 = Location(latitude=52.543861, longitude=13.377130)
    location4 = Location(latitude=52.482568, longitude=13.441025)
    location_repo.add_all([
        location1,
        location2,
        location3,
        location4,
    ])
    coffee_shop1 = PlaceDBCreate(
        name="The Visit Coffee",
        address="Müllerstraße 28, 13353 Berlin",
        location=LocationDB(**location1.model_dump(), id=1),
    )
    coffee_shop2 = PlaceDBCreate(
        name="Coffee Circle Cafe",
        address="Lindower Str. 18, 13347 Berlin",
        location=LocationDB(**location2.model_dump(), id=2),
    )
    coffee_shop3 = PlaceDBCreate(
        name="Flying Roasters",
        address="Hochstraße 34, 13357 Berlin",
        location=LocationDB(**location3.model_dump(), id=3),
    )
    coffee_shop4 = PlaceDBCreate(
        name="The Square",
        address="Wildenbruchstr. 88, 12045 Berlin",
        location=LocationDB(**location4.model_dump(), id=4),
    )
    place_repo.add_all((coffee_shop1, coffee_shop2, coffee_shop3, coffee_shop4))
    session.commit()


@pytest.fixture(name="session")
def session_fixture():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        load_test_data(session)
        yield session


@pytest.fixture
def mock_geocoder(monkeypatch):
    class MockGeocoder:
        def geocode(self, address):
            return Location(latitude=45.45, longitude=54.54)

    def mock_get_geocoder():
        return MockGeocoder()

    monkeypatch.setattr('app.routers.places.get_geocoder', mock_get_geocoder)


@pytest.fixture(name="client")
def client_fixture(session: Session):
    def get_session_override():
        return session
    app.dependency_overrides[SessionDropIn] = get_session_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


def test_create_place(client: TestClient, mock_geocoder, session):
    place_data = {
        "name": "Test Place",
        "address": "123 Test Street",
    }
    response = client.post("/places/", json=place_data)
    place_in_db = PlaceRepository(session).get_all(name=place_data['name'])[0]
    assert response.status_code == 200
    assert response.json()['address'] == "123 Test Street"
    assert place_in_db.address == "123 Test Street"


def test_get_place(client: TestClient, session):
    response = client.get("places/1")
    place = response.json()
    assert place['name'] == "The Visit Coffee"


def test_get_place_404(client: TestClient, session):
    response = client.get("places/101")
    assert response.status_code == 404


def test_get_nearest_places(client: TestClient, session: Session):
    client = TestClient(app)
    response = client.post("/get-nearest/", json={"latitude": 52.550665, "longitude": 13.352322})
    places = response.json()
    assert len(places) == 3
    assert places[0]["name"] == "The Visit Coffee"
    assert places[1]["name"] == "Coffee Circle Cafe"
    assert places[2]["name"] == "Flying Roasters"
