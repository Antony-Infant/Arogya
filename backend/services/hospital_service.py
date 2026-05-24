"""
Hospital Finder using OpenStreetMap Overpass API.
406 fix: Overpass requires proper Content-Type header.
"""
import requests, math, logging
logger = logging.getLogger(__name__)

OVERPASS_MIRRORS = [
    "https://overpass-api.de/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter",
    "https://maps.mail.ru/osm/tools/overpass/api/interpreter",
]


def find_nearby_hospitals(lat: float, lng: float, radius: int = 5000) -> list:
    """Find hospitals, clinics, pharmacies near coordinates using OpenStreetMap."""
    query = (
        f"[out:json][timeout:25];"
        f"("
        f'node["amenity"="hospital"](around:{radius},{lat},{lng});'
        f'way["amenity"="hospital"](around:{radius},{lat},{lng});'
        f'node["amenity"="clinic"](around:{radius},{lat},{lng});'
        f'way["amenity"="clinic"](around:{radius},{lat},{lng});'
        f'node["amenity"="pharmacy"](around:{radius},{lat},{lng});'
        f'node["amenity"="doctors"](around:{radius},{lat},{lng});'
        f");"
        f"out center 20;"
    )
    # 406 fix: Overpass API requires these exact headers
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "application/json",
    }

    last_err = None
    for url in OVERPASS_MIRRORS:
        try:
            r = requests.post(url, data={"data": query},
                              headers=headers, timeout=30)
            if r.status_code == 406:
                logger.warning(f"Overpass 406 at {url} - trying next mirror")
                continue
            if not r.ok:
                logger.warning(f"Overpass {r.status_code} at {url}")
                continue

            results = []
            for el in r.json().get("elements", []):
                tags = el.get("tags", {})
                name = tags.get("name", "").strip()
                if not name:
                    continue
                h_lat = el.get("lat") or el.get("center", {}).get("lat")
                h_lng = el.get("lon") or el.get("center", {}).get("lon")
                if not h_lat or not h_lng:
                    continue
                results.append({
                    "name": name,
                    "type": tags.get("amenity", "hospital"),
                    "lat": h_lat,
                    "lng": h_lng,
                    "phone": tags.get("phone", tags.get("contact:phone", "")),
                    "address": tags.get("addr:full", tags.get("addr:street", "")),
                    "distance_km": round(_km(lat, lng, h_lat, h_lng), 2),
                })
            results.sort(key=lambda x: x["distance_km"])
            logger.info(f"Found {len(results)} facilities near {lat},{lng} via {url}")
            return results[:15]

        except requests.Timeout:
            logger.warning(f"Timeout: {url}")
            last_err = "timeout"
        except Exception as e:
            logger.warning(f"Error {url}: {e}")
            last_err = str(e)

    logger.error(f"All Overpass mirrors failed. Last error: {last_err}")
    return []


def _km(lat1, lon1, lat2, lon2):
    R = 6371
    d = math.radians
    a = (math.sin(d(lat2 - lat1) / 2) ** 2 +
         math.cos(d(lat1)) * math.cos(d(lat2)) *
         math.sin(d(lon2 - lon1) / 2) ** 2)
    return R * 2 * math.asin(math.sqrt(a))


class HospitalService:
    def find_nearby(self, lat, lng, radius=5000):
        return find_nearby_hospitals(lat, lng, radius)
