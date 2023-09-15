import pytest

from app.geocoding import Geocoder, GeocodingError
from app.models import LocationIn
from app.settings import Settings

settings = Settings()


@pytest.fixture()
def geocoder():
    return Geocoder(api_key=settings.geo_api)


def test_location_in_from_address(geocoder: Geocoder):
    address = 'Müllerstraße 28, 13353 Berlin'
    expected = LocationIn(latitude=52.5472567, longitude=13.3580691)
    actual = LocationIn(**geocoder.geocode(address))
    assert expected == actual


def test_location_in_from_address_invalid(geocoder: Geocoder):
    address = 'wo;efuner;gjewrgpowefmiwe'
    with pytest.raises(GeocodingError):
        LocationIn(**geocoder.geocode(address))
