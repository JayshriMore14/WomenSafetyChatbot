"""Location and nearby help center services."""

from __future__ import annotations

from dataclasses import dataclass

import folium
from geopy.distance import geodesic


DEFAULT_LOCATION = (28.6139, 77.2090)  # New Delhi fallback location.


@dataclass
class HelpCenter:
    """Represents a nearby safety help center."""

    name: str
    category: str
    latitude: float
    longitude: float
    phone: str


HELP_CENTERS = [
    HelpCenter("Central Police Station", "Police Station", 28.6200, 77.2150, "100"),
    HelpCenter("City Women Help Desk", "Women Help Center", 28.6085, 77.2058, "1091"),
    HelpCenter("Metro Safety Booth", "Police Station", 28.6178, 77.2122, "112"),
    HelpCenter("General Hospital Emergency", "Hospital", 28.6092, 77.2195, "108"),
    HelpCenter("Community Health Center", "Hospital", 28.6260, 77.2015, "108"),
    HelpCenter("Women Support Center", "Women Help Center", 28.6038, 77.2118, "181"),
]


def get_current_location() -> tuple[float, float]:
    """Return a simulated GPS location."""
    return DEFAULT_LOCATION


def get_location_message(latitude: float, longitude: float) -> str:
    """Create a shareable emergency location message."""
    maps_url = f"https://www.google.com/maps?q={latitude},{longitude}"
    return f"My current location is {latitude:.5f}, {longitude:.5f}. Map: {maps_url}"


def get_nearby_help_centers(latitude: float, longitude: float, limit: int = 6) -> list[dict]:
    """Return help centers sorted by distance from current location."""
    current = (latitude, longitude)
    centers = []
    for center in HELP_CENTERS:
        distance_km = geodesic(current, (center.latitude, center.longitude)).km
        centers.append(
            {
                "name": center.name,
                "category": center.category,
                "latitude": center.latitude,
                "longitude": center.longitude,
                "phone": center.phone,
                "distance_km": round(distance_km, 2),
            }
        )
    return sorted(centers, key=lambda item: item["distance_km"])[:limit]


def build_help_map(latitude: float, longitude: float) -> folium.Map:
    """Build a Folium map with current location and help center markers."""
    safety_map = folium.Map(location=[latitude, longitude], zoom_start=14, tiles="CartoDB positron")
    folium.Marker(
        [latitude, longitude],
        tooltip="Your Current Location",
        popup="Simulated current location",
        icon=folium.Icon(color="blue", icon="user"),
    ).add_to(safety_map)

    colors = {
        "Police Station": "red",
        "Hospital": "green",
        "Women Help Center": "purple",
    }

    for center in get_nearby_help_centers(latitude, longitude):
        folium.Marker(
            [center["latitude"], center["longitude"]],
            tooltip=center["name"],
            popup=f"{center['category']}<br>{center['name']}<br>Phone: {center['phone']}<br>{center['distance_km']} km away",
            icon=folium.Icon(color=colors.get(center["category"], "gray"), icon="info-sign"),
        ).add_to(safety_map)

    return safety_map
