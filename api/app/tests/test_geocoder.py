from unittest.mock import Mock, patch

import pytest

from app.geocoding import Geocoder, GeocodingError
from app.models.places import LocationIn

from .geocoder_responses import features_mueller, features_garbage


def mock_httpx_get(*args, **kwargs):
    address = kwargs['params']['text']
    mock_response = Mock()
    if address == 'Müllerstraße 28, 13353 Berlin':
        mock_response.json.return_value = {'features': features_mueller}
    elif address == 'wo;efuner;gjewrgpowefmiwe':
        mock_response.json.return_value = {'features': features_garbage}
    else:
        mock_response.json.return_value = {'features': []}
    mock_response.status_code = 200
    return mock_response


@pytest.fixture()
def geocoder():
    return Geocoder(api_key='test-key')


def test_location_in_from_address(geocoder: Geocoder):
    address = 'Müllerstraße 28, 13353 Berlin'
    expected = LocationIn(latitude=52.5472567, longitude=13.3580691)
    with patch('httpx.get', side_effect=mock_httpx_get):
        coordinates = geocoder.geocode(address)
    actual = LocationIn(**coordinates)
    assert expected == actual


def test_location_in_from_address_invalid(geocoder: Geocoder):
    address = 'wo;efuner;gjewrgpowefmiwe'
    with pytest.raises(GeocodingError):
        with patch('httpx.get', side_effect=mock_httpx_get):
            geocoder.geocode(address)
