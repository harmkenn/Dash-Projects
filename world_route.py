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
    City("Aarhus", "Denmark", 56.16, 10.21),
    City("Abidjan", "Ivory Coast", 5.36, -4.01),
    City("Almaty", "Kazakhstan", 43.26, 76.93),
    City("Amman", "Jordan", 31.95, 35.93),
    City("Ankara", "Turkey", 39.93, 32.86),
    City("Antananarivo", "Madagascar", -18.88, 47.51),
    City("Apia", "Samoa", -13.83, -171.77),
    City("Asuncion", "Paraguay", -25.28, -57.63),
    City("Baghdad", "Iraq", 33.31, 44.36),
    City("Baku", "Azerbaijan", 40.38, 49.89),
    City("Bamako", "Mali", 12.65, -8.0),
    City("Beirut", "Lebanon", 33.89, 35.5),
    City("Belo Horizonte", "Brazil", -19.92, -43.94),
    City("Bengaluru", "India", 12.97, 77.59),
    City("Bergen", "Norway", 60.39, 5.32),
    City("Birmingham", "United Kingdom", 52.48, -1.89),
    City("Bishkek", "Kyrgyzstan", 42.87, 74.6),
    City("Bordeaux", "France", 44.84, -0.58),
    City("Brasilia", "Brazil", -15.79, -47.88),
    City("Bucharest", "Romania", 44.43, 26.1),
    City("Budapest", "Hungary", 47.5, 19.04),
    City("Busan", "South Korea", 35.18, 129.08),
    City("Cairns", "Australia", -16.92, 145.77),
    City("Calgary", "Canada", 51.05, -114.07),
    City("Canberra", "Australia", -35.28, 149.13),
    City("Cebu City", "Philippines", 10.31, 123.89),
    City("Chengdu", "China", 30.66, 104.07),
    City("Chiang Mai", "Thailand", 18.79, 98.99),
    City("Christchurch", "New Zealand", -43.53, 172.62),
    City("Colombo", "Sri Lanka", 6.93, 79.85),
    City("Cotonou", "Benin", 6.37, 2.42),
    City("Da Nang", "Vietnam", 16.07, 108.22),
    City("Darwin", "Australia", -12.46, 130.84),
    City("Dublin", "Ireland", 53.35, -6.26),
    City("Dunedin", "New Zealand", -45.87, 170.5),
    City("Edinburgh", "United Kingdom", 55.95, -3.19),
    City("Fukuoka", "Japan", 33.59, 130.4),
    City("Galway", "Ireland", 53.27, -9.05),
    City("Geneva", "Switzerland", 46.2, 6.15),
    City("Glasgow", "United Kingdom", 55.86, -4.25),
    City("Guatemala City", "Guatemala", 14.62, -90.53),
    City("Halifax", "Canada", 44.65, -63.58),
    City("Harare", "Zimbabwe", -17.83, 31.05),
    City("Honiara", "Solomon Islands", -9.43, 159.97),
    City("Incheon", "South Korea", 37.48, 126.63),
    City("Jaipur", "India", 26.92, 75.82),
    City("Jerusalem", "Israel", 31.77, 35.21),
    City("Johor Bahru", "Malaysia", 1.49, 103.76),
    City("Kabul", "Afghanistan", 34.53, 69.17),
    City("Kampala", "Uganda", 0.32, 32.58),
    City("Kigali", "Rwanda", -1.95, 30.06),
    City("Kuwait City", "Kuwait", 29.38, 47.98),
    City("Lahore", "Pakistan", 31.55, 74.35),
    City("Luang Prabang", "Laos", 19.89, 102.13),
    City("Lusaka", "Zambia", -15.39, 28.32),
    City("Mandalay", "Myanmar", 21.98, 96.09),
    City("Medan", "Indonesia", 3.59, 98.67),
    City("Milan", "Italy", 45.46, 9.19),
    City("Minsk", "Belarus", 53.9, 27.57),
    City("Munich", "Germany", 48.14, 11.58),
    City("Muscat", "Oman", 23.61, 58.59),
    City("Nadi", "Fiji", -17.76, 177.45),
    City("Nanjing", "China", 32.06, 118.79),
    City("Naples", "Italy", 40.84, 14.25),
    City("Nassau", "Bahamas", 25.05, -77.35),
    City("Nicosia", "Cyprus", 35.18, 33.37),
    City("Papeete", "French Polynesia", -17.54, -149.57),
    City("Peshawar", "Pakistan", 34.01, 71.58),
    City("Port Louis", "Mauritius", -20.16, 57.5),
    City("Port of Spain", "Trinidad and Tobago", 10.65, -61.52),
    City("Pretoria", "South Africa", -25.75, 28.24),
    City("Qingdao", "China", 36.07, 120.38),
    City("Rabat", "Morocco", 34.02, -6.84),
    City("Riga", "Latvia", 56.95, 24.11),
    City("Salvador", "Brazil", -12.97, -38.51),
    City("Sanaa", "Yemen", 15.35, 44.21),
    City("San Jose", "Costa Rica", 9.93, -84.08),
    City("San Juan", "Puerto Rico", 18.47, -66.11),
    City("Santiago de los Caballeros", "Dominican Republic", 19.47, -70.7),
    City("Sapporo", "Japan", 43.06, 141.35),
    City("Seville", "Spain", 37.39, -5.99),
    City("Sofia", "Bulgaria", 42.7, 23.32),
    City("Surabaya", "Indonesia", -7.26, 112.74),
    City("Tbilisi", "Georgia", 41.71, 44.83),
    City("Tegucigalpa", "Honduras", 14.08, -87.21),
    City("Tirana", "Albania", 41.33, 19.82),
    City("Tripoli", "Libya", 32.89, 13.19),
    City("Ulaanbaatar", "Mongolia", 47.92, 106.92),
    City("Valencia", "Spain", 39.47, -0.38),
    City("Vientiane", "Laos", 17.97, 102.61),
    City("Wellington", "New Zealand", -41.29, 174.78),
    City("Yerevan", "Armenia", 40.18, 44.51),
    City("Zagreb", "Croatia", 45.81, 15.98),
    City("Zurich", "Switzerland", 47.37, 8.54),
    City("Adelaide", "Australia", -34.93, 138.6),
    City("Belfast", "United Kingdom", 54.6, -5.93),
    City("Cordoba", "Argentina", -31.42, -64.19),
    City("Freetown", "Sierra Leone", 8.48, -13.23),
    City("Gdansk", "Poland", 54.35, 18.65),
    City("Izmir", "Turkey", 38.42, 27.14),
    City("Ljubljana", "Slovenia", 46.05, 14.51),
    City("Luanda", "Angola", -8.84, 13.23),
    City("Marrakech", "Morocco", 31.63, -7.99),
    City("New Orleans", "United States", 29.95, -90.07),
    City("Omaha", "United States", 41.26, -95.94),
    City("Ponta Delgada", "Portugal", 37.77, -25.67),
    City("Porto Alegre", "Brazil", -30.03, -51.23),
    City("Saint Petersburg", "Russia", 59.93, 30.31),
    City("Shenzhen", "China", 22.55, 114.06),
    City("Tashkent", "Uzbekistan", 41.26, 69.22),
    City("Xi'an", "China", 34.27, 108.95),
    City("Harbin", "China", 45.75, 126.63),
    City("Marseille", "France", 43.3, 5.37),
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
