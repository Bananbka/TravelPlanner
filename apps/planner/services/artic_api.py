import requests
from django.core.cache import cache
from rest_framework.exceptions import ValidationError

ARTIC_BASE_URL = "https://api.artic.edu/api/v1"


def validate_place_exists(external_id: str) -> bool:
    cache_key = f"artic_place_{external_id}"
    cached_result = cache.get(cache_key)

    if cached_result is not None:
        return cached_result

    url = f"{ARTIC_BASE_URL}/artworks/{external_id}"

    try:
        response = requests.get(url, params={"fields": "id"})

        if response.status_code == 200:
            cache.set(cache_key, True, timeout=86400)
            return True
        elif response.status_code == 404:
            cache.set(cache_key, False, timeout=86400)
            return False

        response.raise_for_status()
    except requests.RequestException:
        raise ValidationError("Third-party API is currently unavailable.")

    return False


def search_places(query: str, limit: int = 10) -> list:
    url = f"{ARTIC_BASE_URL}/artworks/search"

    params = {
        "q": query,
        "limit": limit,
        "fields": "id,title,description"
    }

    try:
        response = requests.get(url, params=params, timeout=5)
        response.raise_for_status()

        return response.json().get('data', [])
    except requests.RequestException as e:
        raise ValidationError("Third-party API is currently unavailable.")
