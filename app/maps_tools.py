import json
import os
from pathlib import Path
import urllib.parse
import urllib.request
from dotenv import load_dotenv

# Ensure .env variables are loaded
env_path = Path(__file__).resolve().parent.parent / ".env"
if env_path.exists():
    load_dotenv(dotenv_path=env_path)


def geocode_address(address: str) -> str:
    """Turns a street address or location name into geographic coordinates (latitude/longitude) using Google Geocoding API.

    Args:
        address: The location address or landmark name (e.g. 'Eiffel Tower, Paris' or 'Shibuya Crossing, Tokyo').

    Returns:
        A JSON string containing the formatted address, latitude, and longitude.
    """
    api_key = os.getenv("GOOGLE_MAPS_API_KEY")
    if not api_key:
        return "Error: GOOGLE_MAPS_API_KEY environment variable is not set."

    encoded_address = urllib.parse.quote(address)
    url = f"https://maps.googleapis.com/maps/api/geocode/json?address={encoded_address}&key={api_key}"

    try:
        req = urllib.request.Request(url, headers={"User-Agent": "TravelPlannerAgent/1.0"})
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode())
            if data.get("status") != "OK" or not data.get("results"):
                return f"Geocoding failed for address '{address}': {data.get('status', 'No results')}"

            result = data["results"][0]
            location = result["geometry"]["location"]
            return json.dumps(
                {
                    "query": address,
                    "formatted_address": result.get("formatted_address"),
                    "latitude": location["lat"],
                    "longitude": location["lng"],
                },
                indent=2,
            )
    except Exception as e:
        return f"Error executing Geocoding API request: {str(e)}"


def find_nearby_places(
    latitude: float,
    longitude: float,
    place_type: str = "tourist_attraction",
    radius_meters: float = 3000.0,
) -> str:
    """Finds nearby places (attractions, restaurants, hotels) around coordinates using Places API (New).

    Args:
        latitude: Center latitude coordinate.
        longitude: Center longitude coordinate.
        place_type: Type of place to search for (e.g., 'tourist_attraction', 'restaurant', 'lodging', 'museum').
        radius_meters: Search radius in meters (default is 3000 meters).

    Returns:
        A JSON string listing nearby places with key fields: name, address, and location.
    """
    api_key = os.getenv("GOOGLE_MAPS_API_KEY")
    if not api_key:
        return "Error: GOOGLE_MAPS_API_KEY environment variable is not set."

    url = "https://places.googleapis.com/v1/places:searchNearby"
    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": api_key,
        "X-Goog-FieldMask": "places.displayName,places.formattedAddress,places.location",
    }
    payload = {
        "includedTypes": [place_type],
        "maxResultCount": 5,
        "locationRestriction": {
            "circle": {
                "center": {"latitude": latitude, "longitude": longitude},
                "radius": float(radius_meters),
            }
        },
    }

    try:
        body = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(url, data=body, headers=headers, method="POST")
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode())
            places = data.get("places", [])

            results = []
            for p in places:
                display_name = p.get("displayName", {}).get("text", "Unknown Place")
                results.append(
                    {
                        "name": display_name,
                        "address": p.get("formattedAddress"),
                        "location": p.get("location"),
                    }
                )

            if not results:
                return f"No nearby places found of type '{place_type}' within {radius_meters} meters."

            return json.dumps(results, indent=2)
    except Exception as e:
        return f"Error executing Places API (New) request: {str(e)}"
