from dataclasses import dataclass
from math import asin, cos, radians, sin, sqrt


@dataclass(frozen=True)
class City:
    name: str
    country: str
    latitude: float
    longitude: float

    @property
    def label(self):
        return f"{self.name}, {self.country}"


CITIES = (
    City("Auckland", "New Zealand", -36.85, 174.76),
    City("Sydney", "Australia", -33.87, 151.21),
    City("Melbourne", "Australia", -37.81, 144.96),
    City("Brisbane", "Australia", -27.47, 153.03),
    City("Perth", "Australia", -31.95, 115.86),
    City("Tokyo", "Japan", 35.68, 139.69),
    City("Osaka", "Japan", 34.69, 135.50),
    City("Seoul", "South Korea", 37.57, 126.98),
    City("Shanghai", "China", 31.23, 121.47),
    City("Beijing", "China", 39.90, 116.40),
    City("Hong Kong", "China", 22.32, 114.17),
    City("Taipei", "Taiwan", 25.03, 121.57),
    City("Manila", "Philippines", 14.60, 120.98),
    City("Singapore", "Singapore", 1.35, 103.82),
    City("Bangkok", "Thailand", 13.76, 100.50),
    City("Hanoi", "Vietnam", 21.03, 105.85),
    City("Ho Chi Minh City", "Vietnam", 10.82, 106.63),
    City("Jakarta", "Indonesia", -6.21, 106.85),
    City("Kuala Lumpur", "Malaysia", 3.14, 101.69),
    City("Phnom Penh", "Cambodia", 11.56, 104.93),
    City("Delhi", "India", 28.61, 77.21),
    City("Mumbai", "India", 19.08, 72.88),
    City("Kolkata", "India", 22.57, 88.36),
    City("Karachi", "Pakistan", 24.86, 67.01),
    City("Kathmandu", "Nepal", 27.72, 85.32),
    City("Dhaka", "Bangladesh", 23.81, 90.41),
    City("Dubai", "United Arab Emirates", 25.20, 55.27),
    City("Doha", "Qatar", 25.29, 51.53),
    City("Riyadh", "Saudi Arabia", 24.71, 46.68),
    City("Tehran", "Iran", 35.69, 51.39),
    City("Istanbul", "Turkey", 41.01, 28.98),
    City("Athens", "Greece", 37.98, 23.73),
    City("Cairo", "Egypt", 30.04, 31.24),
    City("Nairobi", "Kenya", -1.29, 36.82),
    City("Addis Ababa", "Ethiopia", 8.98, 38.76),
    City("Dar es Salaam", "Tanzania", -6.79, 39.21),
    City("Cape Town", "South Africa", -33.92, 18.42),
    City("Johannesburg", "South Africa", -26.20, 28.04),
    City("Lagos", "Nigeria", 6.52, 3.38),
    City("Accra", "Ghana", 5.60, -0.19),
    City("Dakar", "Senegal", 14.72, -17.47),
    City("Casablanca", "Morocco", 33.57, -7.59),
    City("Algiers", "Algeria", 36.75, 3.06),
    City("Reykjavik", "Iceland", 64.15, -21.94),
    City("London", "United Kingdom", 51.51, -0.13),
    City("Paris", "France", 48.86, 2.35),
    City("Amsterdam", "Netherlands", 52.37, 4.90),
    City("Brussels", "Belgium", 50.85, 4.35),
    City("Copenhagen", "Denmark", 55.68, 12.57),
    City("Stockholm", "Sweden", 59.33, 18.07),
    City("Oslo", "Norway", 59.91, 10.75),
    City("Helsinki", "Finland", 60.17, 24.94),
    City("Madrid", "Spain", 40.42, -3.70),
    City("Lisbon", "Portugal", 38.72, -9.14),
    City("Rome", "Italy", 41.90, 12.50),
    City("Vienna", "Austria", 48.21, 16.37),
    City("Prague", "Czechia", 50.08, 14.44),
    City("Berlin", "Germany", 52.52, 13.41),
    City("Moscow", "Russia", 55.76, 37.62),
    City("Kyiv", "Ukraine", 50.45, 30.52),
    City("New York", "United States", 40.71, -74.01),
    City("Toronto", "Canada", 43.65, -79.38),
    City("Montreal", "Canada", 45.50, -73.57),
    City("Chicago", "United States", 41.88, -87.63),
    City("Miami", "United States", 25.76, -80.19),
    City("Seattle", "United States", 47.61, -122.33),
    City("Washington, D.C.", "United States", 38.91, -77.04),
    City("Havana", "Cuba", 23.11, -82.37),
    City("Panama City", "Panama", 8.98, -79.52),
    City("Mexico City", "Mexico", 19.43, -99.13),
    City("Bogota", "Colombia", 4.71, -74.07),
    City("Quito", "Ecuador", -0.18, -78.47),
    City("Caracas", "Venezuela", 10.48, -66.90),
    City("Lima", "Peru", -12.05, -77.04),
    City("La Paz", "Bolivia", -16.49, -68.12),
    City("Santiago", "Chile", -33.45, -70.67),
    City("Buenos Aires", "Argentina", -34.60, -58.38),
    City("Montevideo", "Uruguay", -34.90, -56.19),
    City("Sao Paulo", "Brazil", -23.56, -46.64),
    City("Rio de Janeiro", "Brazil", -22.91, -43.17),
    City("Anchorage", "United States", 61.22, -149.90),
    City("Los Angeles", "United States", 34.05, -118.24),
    City("San Francisco", "United States", 37.77, -122.42),
    City("Vancouver", "Canada", 49.28, -123.12),
    City("Honolulu", "United States", 21.31, -157.86),
    City("Suva", "Fiji", -18.14, 178.44),
    City("Port Moresby", "Papua New Guinea", -9.44, 147.18),
)

MIN_LEGS = 2
MAX_LEGS = 20
EARTH_RADIUS_KM = 6371.0088


def _longitude_distance(first, second):
    return abs((first - second + 180) % 360 - 180)


def haversine_km(first, second):
    latitude_1, latitude_2 = radians(first.latitude), radians(second.latitude)
    latitude_delta = latitude_2 - latitude_1
    longitude_delta = radians(second.longitude - first.longitude)
    haversine = (
        sin(latitude_delta / 2) ** 2
        + cos(latitude_1) * cos(latitude_2) * sin(longitude_delta / 2) ** 2
    )
    return 2 * EARTH_RADIUS_KM * asin(sqrt(haversine))


def build_route(start_name, leg_count):
    """Choose evenly spaced longitude stops and close the route at its start."""
    if not isinstance(leg_count, int) or isinstance(leg_count, bool):
        raise ValueError(f"Choose between {MIN_LEGS} and {MAX_LEGS} route legs.")
    if not MIN_LEGS <= leg_count <= min(MAX_LEGS, len(CITIES)):
        raise ValueError(f"Choose between {MIN_LEGS} and {min(MAX_LEGS, len(CITIES))} route legs.")

    cities_by_name = {city.name: city for city in CITIES}
    if start_name not in cities_by_name:
        raise ValueError("Choose a starting city from the list.")

    start = cities_by_name[start_name]
    route = [start]
    selected_names = {start.name}
    for index in range(1, leg_count):
        target_longitude = start.longitude + 360 * index / leg_count
        next_city = min(
            (city for city in CITIES if city.name not in selected_names),
            key=lambda city: (
                _longitude_distance(city.longitude, target_longitude),
                haversine_km(start, city),
                city.name,
            ),
        )
        route.append(next_city)
        selected_names.add(next_city.name)

    route.append(start)
    return route


def route_distance_km(route):
    return sum(haversine_km(first, second) for first, second in zip(route, route[1:]))
