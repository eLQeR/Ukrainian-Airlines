import datetime
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Count, F

from airlines_api.models import Airport, AirplaneType, Route, Flight, Airplane, Crew
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient, override_settings
from user.models import User
from airlines_api.serializers import (
    FlightListSerializer,
    FlightSerializer,
    FlightDetailSerializer,
    FlightAdminDetailSerializer,
)

FLIGHT_URL = "/api/airlines/flights/"
TRANSFER_URL = "/api/airlines/get-ways/"


def sample_flights(num_flights: int = 5):
    for i in range(num_flights):
        airport1 = Airport.objects.create(
            name=f"Test-{i} Source Airport",
            closest_big_city=f"Test{-i} destination City"
        )
        airport2 = Airport.objects.create(
            name=f"Test-{i} Destination Airport",
            closest_big_city=f"Test-{i} Destination City"
        )
        route = Route.objects.create(
            source=airport1,
            destination=airport2,
            distance=1000,
        )
        airplane_type = AirplaneType.objects.create(name="Boeing")
        airplane = Airplane.objects.create(
            name="Boeing 377",
            rows=10,
            seats_in_row=10,
            airplane_type=airplane_type,
        )
        Flight.objects.create(
            route=route,
            airplane=airplane,
            departure_time=datetime.datetime.strptime(f"2024-04-1{i}T12:55:00", "%Y-%m-%dT%H:%M:%S"),
            arrival_time=datetime.datetime.strptime(f"2024-04-1{i + 1}T02:55:00", "%Y-%m-%dT%H:%M:%S")
        )


def get_annotated_flights(queryset):
    return queryset.annotate(
            tickets_avaliable=(
                (F("airplane__rows") * F("airplane__seats_in_row")) - Count('tickets')
            )
        )

class AuthenticatedUserApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

        sample_flights()

        self.first_flight = Flight.objects.first()

        user = User.objects.create_user(username='user', password='<PASSWORD>')

        self.data = {
            "route": 1,
            "airplane": 1,
            "departure_time": datetime.datetime.strptime(
                f"2025-04-11T12:55:00", "%Y-%m-%dT%H:%M:%S"
            ),
            "arrival_time": datetime.datetime.strptime(
                f"2025-04-12T12:55:00", "%Y-%m-%dT%H:%M:%S"
            )
        }

        self.client.force_authenticate(user=user)

    def test_get_flights(self):
        response = self.client.get(FLIGHT_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for i in range(len(response.data["results"])):
            flight = response.data["results"][i]
            self.assertEqual(
                flight['id'], i + 1
            )
            self.assertEqual(
                flight['departure_time'], f"2024-04-1{i}T12:55:00"
            )
            self.assertEqual(
                flight['arrival_time'], f"2024-04-1{i + 1}T02:55:00"
            )
            self.assertEqual(
                flight['time_of_flight'], "14:00:00"
            )
            self.assertEqual(
                flight['airplane'], "Boeing 377"
            )

    def test_get_flights_annotated(self):
        response = self.client.get(FLIGHT_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        flights = get_annotated_flights(Flight.objects.all())

        self.assertEqual(response.data["results"], FlightListSerializer(flights, many=True).data)

    def test_filtered_flights_by_route(self):
        response = self.client.get(f"{FLIGHT_URL}?route=1")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data["results"],
            FlightListSerializer(
                get_annotated_flights(Flight.objects.filter(route_id=1)), many=True
            ).data
        )

    def test_filtered_flights_by_departure_time(self):
        response = self.client.get(f"{FLIGHT_URL}?departure_date=2024-04-11")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data["results"],
            FlightListSerializer(
                get_annotated_flights(Flight.objects.filter(departure_time__date="2024-04-11")), many=True
            ).data
        )

    def test_create_flight_forbidden(self):
        response = self.client.post(FLIGHT_URL, self.data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertRaises(ObjectDoesNotExist, Flight.objects.get, departure_time__date="2025-04-11")

    def test_update_flight_forbidden(self):
        response = self.client.put(f"{FLIGHT_URL}1/", self.data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertRaises(ObjectDoesNotExist, Flight.objects.get, departure_time__date="2025-04-11")

    def test_delete_flight_forbidden(self):
        response = self.client.delete(
            f"{FLIGHT_URL}1/",
        )
        db_flight_id_1 = Flight.objects.filter(pk=1)

        self.assertEqual(db_flight_id_1.count(), 1)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_retrieve_flight(self):
        response = self.client.get(f"{FLIGHT_URL}1/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        flight = get_annotated_flights(Flight.objects.filter(pk=1))[0]
        serialized_flight = FlightDetailSerializer(flight).data

        self.assertEqual(
            response.data.pop("airplane")["id"],
            serialized_flight.pop("airplane")["id"],

        )
        self.assertEqual(
            response.data,
            serialized_flight
        )

    def test_get_invalid_flight(self):
        response = self.client.get(f"{FLIGHT_URL}1001/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class UnauthenticatedUserApiTests(AuthenticatedUserApiTests):
    def setUp(self):
        super().setUp()
        self.client.logout()

    def test_create_flight_forbidden(self):
        response = self.client.post(FLIGHT_URL, self.data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_flight_forbidden(self):
        response = self.client.put(f"{FLIGHT_URL}1/", self.data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_flight_forbidden(self):
        response = self.client.delete(
            f"{FLIGHT_URL}1/",
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class AdminApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

        sample_flights()

        self.first_flight = Flight.objects.first()

        user = User.objects.create_superuser(username='Admin_user', password='<PASSWORD>')

        self.data = {
            "route": 1,
            "airplane": 1,
            "departure_time": datetime.datetime.strptime(
                f"2025-04-11T12:55:00", "%Y-%m-%dT%H:%M:%S"
            ),
            "arrival_time": datetime.datetime.strptime(
                f"2025-04-12T12:55:00", "%Y-%m-%dT%H:%M:%S"
            )
        }

        self.client.force_authenticate(user=user)

    def test_create_flight(self):
        response = self.client.post(FLIGHT_URL, self.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Flight.objects.count(), 6)
        self.assertEqual(
            response.data,
            FlightSerializer(
                Flight.objects.get(departure_time__date="2025-04-11")
            ).data
        )

    def test_update_flight(self):
        response = self.client.put(f"{FLIGHT_URL}1/", self.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data,
            FlightSerializer(
                Flight.objects.get(departure_time__date="2025-04-11")
            ).data
        )

    def test_delete_flight(self):
        response = self.client.delete(
            f"{FLIGHT_URL}1/",
        )
        db_flight_id_1 = Flight.objects.filter(pk=1)

        self.assertEqual(db_flight_id_1.count(), 0)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_invalid_airport(self):
        response = self.client.delete(
            f"{FLIGHT_URL}1001/",
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class TransferFlightsApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

        sample_flights(num_flights=9)

        self.airport1 = Airport.objects.create(
            name=f"Test-1 Source Airport",
            closest_big_city=f"Test-1 destination City"
        )
        self.airport2 = Airport.objects.create(
            name=f"Test-2 Destination Airport",
            closest_big_city=f"Test-2 Destination City"
        )
        self.airport3 = Airport.objects.create(
            name=f"Test-2 Destination Airport",
            closest_big_city=f"Test-2 Destination City"
        )
        self.route_a1_to_a2 = Route.objects.create(
            source=self.airport1,
            destination=self.airport2,
            distance=1000,
        )

        self.route_a2_to_a3 = Route.objects.create(
            source=self.airport2,
            destination=self.airport3,
            distance=1000,
        )

        self.airplane_type = AirplaneType.objects.create(name="Boeing")
        airplane = Airplane.objects.create(
            name="Boeing 377",
            rows=10,
            seats_in_row=10,
            airplane_type=self.airplane_type,
        )
        for day in range(1, 8):
            Flight.objects.create(
                route=self.route_a1_to_a2,
                airplane=airplane,
                departure_time=datetime.datetime.strptime(f"2025-04-1{day}T12:55:00", "%Y-%m-%dT%H:%M:%S"),
                arrival_time=datetime.datetime.strptime(f"2025-04-1{day + 1}T2:55:00", "%Y-%m-%dT%H:%M:%S")

            )
            Flight.objects.create(
                route=self.route_a2_to_a3,
                airplane=airplane,
                departure_time=datetime.datetime.strptime(f"2025-04-1{day + 1}T04:00:00", "%Y-%m-%dT%H:%M:%S"),
                arrival_time=datetime.datetime.strptime(f"2025-04-1{day + 2}T00:55:00", "%Y-%m-%dT%H:%M:%S")

            )
        self.flight_from_a1_to_a2 = Flight.objects.filter(route=self.route_a1_to_a2).order_by('id')[0]
        self.flight_from_a2_to_a3 = Flight.objects.filter(route=self.route_a2_to_a3).order_by('id')[0]

        self.data = {
            "route": 1,
            "airplane": 1,
            "departure_time": datetime.datetime.strptime(
                f"2025-04-11T12:55:00", "%Y-%m-%dT%H:%M:%S"
            ),
            "arrival_time": datetime.datetime.strptime(
                f"2025-04-12T2:55:00", "%Y-%m-%dT%H:%M:%S"
            )
        }

    def test_get_transfer_flights(self):
        response = self.client.get(
            f"{TRANSFER_URL}?date=2025-04-11&airport1={self.airport1.id}&airport2={self.airport3.id}",
        )
        flights = {
            "result": [FlightListSerializer(
                (self.flight_from_a1_to_a2, self.flight_from_a2_to_a3),
                many=True
            ).data]
        }

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, flights)

    def test_no_flights_on_date(self):
        response = self.client.get(
            f"{TRANSFER_URL}?date=2025-04-08&airport1={self.airport1.id}&airport2={self.airport3.id}",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data,
            {
                "result": f"There are no any flight from {self.airport1.name}"
                          f" to {self.airport2.name} in 2025-04-08"
             }
        )

    def test_with_second_destination_flight(self):
        second_destination_flight = Flight.objects.create(
            route=self.route_a2_to_a3,
            airplane=Airplane.objects.create(
                name="Second Test Airplane",
                rows=10, seats_in_row=10,
                airplane_type=self.airplane_type
            ),
            departure_time=datetime.datetime.strptime(
                "2025-04-12T22:25:00", "%Y-%m-%dT%H:%M:%S"
            ),
            arrival_time=datetime.datetime.strptime(
                "2025-04-13T4:55:00", "%Y-%m-%dT%H:%M:%S"
            )
        )
        response = self.client.get(
            f"{TRANSFER_URL}?date=2025-04-11&airport1={self.airport1.id}&airport2={self.airport3.id}",
        )
        transfer_flights = (
            (self.flight_from_a1_to_a2, self.flight_from_a2_to_a3),
            (self.flight_from_a1_to_a2, second_destination_flight),
        )
        flights = {
            "result": [
                FlightListSerializer(flights, many=True).data
                for flights in transfer_flights
            ]
        }

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, flights)

    def test_with_second_source_flight(self):
        second_source_flight = Flight.objects.create(
            route=self.route_a1_to_a2,
            airplane=Airplane.objects.create(
                name="Second Test Airplane",
                rows=10, seats_in_row=10,
                airplane_type=self.airplane_type
            ),
            departure_time=datetime.datetime.strptime(
                "2025-04-11T08:25:00", "%Y-%m-%dT%H:%M:%S"
            ),
            arrival_time=datetime.datetime.strptime(
                "2025-04-11T22:55:00", "%Y-%m-%dT%H:%M:%S"
            )
        )
        response = self.client.get(
            f"{TRANSFER_URL}?date=2025-04-11&airport1={self.airport1.id}&airport2={self.airport3.id}",
        )
        transfer_flights = (
            (second_source_flight, self.flight_from_a2_to_a3),
            (self.flight_from_a1_to_a2, self.flight_from_a2_to_a3),
        )
        flights = {
            "result": [
                FlightListSerializer(flights, many=True).data
                for flights in transfer_flights
            ]
        }

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, flights)

    def test_get_right_flight(self):
        response = self.client.get(
            f"{TRANSFER_URL}?date=2025-04-11&airport1={self.airport1.id}&airport2={self.airport2.id}",
        )
        date = datetime.datetime.strptime("2025-04-11", "%Y-%m-%d")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        flights = Flight.objects.filter(
            route=self.route_a1_to_a2,
            departure_time__gt=date,
            departure_time__lt=date + datetime.timedelta(days=2)

        )
        self.assertEqual(
            response.data,
            {"result": FlightListSerializer(flights, many=True).data}
        )
