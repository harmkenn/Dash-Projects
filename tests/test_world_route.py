import unittest

from world_route import CITIES, MAX_LEGS, MIN_LEGS, build_route, route_distance_km


class BuildRouteTests(unittest.TestCase):
    def test_route_has_requested_legs_and_returns_to_start(self):
        for leg_count in (MIN_LEGS, 6, MAX_LEGS):
            with self.subTest(leg_count=leg_count):
                route = build_route("London", leg_count)
                self.assertEqual(len(route) - 1, leg_count)
                self.assertEqual(route[0], route[-1])
                self.assertEqual(len({city.name for city in route[:-1]}), leg_count)

    def test_selected_cities_follow_even_eastward_longitude_targets(self):
        start_name = "London"
        leg_count = 6
        route = build_route(start_name, leg_count)
        start = route[0]
        relative_longitudes = [
            (city.longitude - start.longitude) % 360 for city in route[:-1]
        ]
        self.assertEqual(relative_longitudes[0], 0)
        self.assertEqual(relative_longitudes, sorted(relative_longitudes))
        for index, city in enumerate(route[1:-1], start=1):
            target = 360 * index / leg_count
            actual = (city.longitude - start.longitude) % 360
            self.assertLessEqual(abs(actual - target), 30)

    def test_all_starting_cities_produce_unique_closed_routes(self):
        self.assertGreaterEqual(len(CITIES), 80)
        for city in CITIES:
            with self.subTest(start=city.name):
                for leg_count in (MIN_LEGS, MAX_LEGS):
                    route = build_route(city.name, leg_count)
                    self.assertEqual(route[0], city)
                    self.assertEqual(route[0], route[-1])
                    self.assertEqual(len(route) - 1, leg_count)
                    self.assertEqual(len({stop.name for stop in route[:-1]}), leg_count)
                    self.assertGreater(route_distance_km(route), 0)

    def test_max_leg_routes_progress_around_the_globe(self):
        for city in CITIES:
            with self.subTest(start=city.name):
                route = build_route(city.name, MAX_LEGS)
                relative_longitudes = [
                    (stop.longitude - city.longitude) % 360 for stop in route[:-1]
                ]
                self.assertEqual(relative_longitudes, sorted(relative_longitudes))

    def test_invalid_start_and_leg_counts_are_rejected(self):
        with self.assertRaisesRegex(ValueError, "starting city"):
            build_route("Atlantis", 4)
        for leg_count in (MIN_LEGS - 1, MAX_LEGS + 1, 3.5, True):
            with self.subTest(leg_count=leg_count):
                with self.assertRaises(ValueError):
                    build_route("London", leg_count)


if __name__ == "__main__":
    unittest.main()
