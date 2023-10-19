import httpx

from models import Place


class PlacesClient:
    def __init__(self, api_url):
        self.api_url = api_url

    def get_nearest_places(self, latitude: float, longitude: float):
        payload = {'latitude': latitude, 'longitude': longitude}
        response = httpx.post(self.api_url, json=payload)
        response.raise_for_status()
        return [Place(**loc) for loc in response.json()]
