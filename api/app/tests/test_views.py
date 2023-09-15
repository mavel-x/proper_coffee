import pytest
from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, create_engine, SQLModel

from app.models import Location, Place
from app.main import app, get_db_session


@pytest.fixture(name="session")
def session_fixture():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(session: Session):
    def get_session_override():
        return session
    app.dependency_overrides[get_db_session] = get_session_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


def test_get_nearest_places(client: TestClient, session: Session):
    location1 = Location(latitude=52.547250, longitude=13.358090)
    location2 = Location(latitude=52.543880, longitude=13.367920)
    location3 = Location(latitude=52.543861, longitude=13.377130)
    location4 = Location(latitude=52.482568, longitude=13.441025)

    session.add(location1)
    session.add(location2)
    session.add(location3)
    session.add(location4)
    session.commit()

    coffee_shop1 = Place(
        name="The Visit Coffee",
        address="Müllerstraße 28, 13353 Berlin",
        location_id=location1.id
    )
    coffee_shop2 = Place(
        name="Coffee Circle Cafe",
        address="Lindower Str. 18, 13347 Berlin",
        location_id=location2.id
    )
    coffee_shop3 = Place(
        name="Flying Roasters",
        address="Hochstraße 34, 13357 Berlin",
        location_id=location3.id
    )
    coffee_shop4 = Place(
        name="The Square",
        address="Wildenbruchstr. 88, 12045 Berlin",
        location_id=location4.id
    )

    session.add(coffee_shop1)
    session.add(coffee_shop2)
    session.add(coffee_shop3)
    session.add(coffee_shop4)
    session.commit()

    client = TestClient(app)
    response = client.post("/get-nearest/", json={"latitude": 52.550665, "longitude": 13.352322})

    assert response.status_code == 200
    places = response.json()
    assert len(places) == 3
    assert places[0]["name"] == "The Visit Coffee"
    assert places[1]["name"] == "Coffee Circle Cafe"
    assert places[2]["name"] == "Flying Roasters"
