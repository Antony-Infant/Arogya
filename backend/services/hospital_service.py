"""
Hospital Finder - Uses OpenStreetMap Overpass API to find nearby hospitals.
Free, no API key needed, works worldwide.
"""
import requests
import math
import logging

logger = logging.getLogger(__name__)

class HospitalService:
    OVERPASS_URL = "https://overpass-api.de/api/interpreter"

    def find_nearby(self, lat: float, lng: float, radius: int = 5000) -> list:
        """Find hospitals, clinics, and pharmacies near given coordinates."""
        query = f"""
        [out:json][timeout:25];
        (
            node["amenity"="hospital"](around:{radius},{lat},{lng});
            way["amenity"="hospital"](around:{radius},{lat},{lng});
            node["amenity"="clinic"](around:{radius},{lat},{lng});
            way["amenity"="clinic"](around:{radius},{lat},{lng});
            node["amenity"="pharmacy"](around:{radius},{lat},{lng});
        );
        out center 20;
        """

        try:
            response = requests.post(self.OVERPASS_URL, data={'data': query}, timeout=30)
            if response.status_code != 200:
                logger.error(f"Overpass API error: {response.status_code}")
                return []

            results = []
            for element in response.json().get('elements', []):
                tags = element.get('tags', {})
                h_lat = element.get('lat') or element.get('center', {}).get('lat')
                h_lng = element.get('lon') or element.get('center', {}).get('lon')

                if h_lat and h_lng:
                    distance = self._haversine(lat, lng, h_lat, h_lng)
                    results.append({
                        'name': tags.get('name', 'Medical Facility'),
                        'type': tags.get('amenity', 'hospital'),
                        'lat': h_lat,
                        'lng': h_lng,
                        'phone': tags.get('phone', ''),
                        'address': tags.get('addr:full', tags.get('addr:street', '')),
                        'emergency': tags.get('emergency', ''),
                        'distance_km': round(distance, 2),
                    })

            results.sort(key=lambda x: x['distance_km'])
            return results[:15]

        except Exception as e:
            logger.error(f"Hospital finder error: {e}")
            return []

    def _haversine(self, lat1, lon1, lat2, lon2) -> float:
        R = 6371  # Earth radius in km
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
        return R * 2 * math.asin(math.sqrt(a))
