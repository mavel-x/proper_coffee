import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, create_engine, SQLModel

from models import Location, Place
from main import app


engine = create_engine('sqlite:///:memory:')


@pytest.fixture()
def test_session():
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session
    SQLModel.metadata.drop_all(engine)


def test_get_nearest_coffee_shops(test_session):
    location1 = Location(latitude=52.547250, longitude=13.358090)
    location2 = Location(latitude=52.543880, longitude=13.367920)
    location3 = Location(latitude=52.543861, longitude=13.377130)

    test_session.add(location1)
    test_session.add(location2)
    test_session.add(location3)
    test_session.commit()

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

    test_session.add(coffee_shop1)
    test_session.add(coffee_shop2)
    test_session.add(coffee_shop3)
    test_session.commit()

    client = TestClient(app)
    response = client.post("/get-nearest/", json={"latitude": 52.550665, "longitude": 13.352322})

    assert response.status_code == 200
    assert len(response.json()) == 3
    assert response.json()[0]["name"] == "The Visit Coffee"
    assert response.json()[1]["name"] == "Coffee Circle Cafe"
    assert response.json()[2]["name"] == "Flying Roasters"
