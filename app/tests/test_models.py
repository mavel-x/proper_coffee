import pytest

from models import LocationIn
from settings import Settings

settings = Settings(_env_file='../../.env')


def test_location_in_from_address():
    address = 'Müllerstraße 28, 13353 Berlin'
    expected = LocationIn(latitude=52.5472567, longitude=13.3580691)
    actual = LocationIn.from_address(address, settings.geo_api)
    assert expected == actual


def test_location_in_from_address_invalid():
    address = 'wo;efuner;gjewrgpowefmiwe'
    with pytest.raises(ValueError):
        LocationIn.from_address(address, settings.geo_api)
