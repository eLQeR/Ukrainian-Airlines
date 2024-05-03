import datetime
from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError
from django.db.models import Count, F
from rest_framework.exceptions import ErrorDetail

from airlines_api.models import Flight, Ticket, Order, Route, AirplaneType, Airplane, Airport, Passenger
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient
from user.models import User
from airlines_api.serializers import OrderSerializer, OrderListSerializer

ORDER_URL = "/api/airlines/orders/"


def sample_flight():
    airport1 = Airport.objects.create(
        name=f"Test-Source Airport",
        closest_big_city=f"Test destination City"
    )
    airport2 = Airport.objects.create(
        name=f"Test-Destination Airport",
        closest_big_city=f"Test Destination City"
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
    return (
        Flight.objects.create(
            route=route,
            airplane=airplane,
            departure_time=datetime.datetime.strptime(
                f"2024-04-10T12:55:00",
                "%Y-%m-%dT%H:%M:%S"
            ),
            arrival_time=datetime.datetime.strptime(
                f"2024-04-11T02:55:00",
                "%Y-%m-%dT%H:%M:%S"
            )
        )
    )


def sample_passenger():
    return Passenger.objects.create(
        first_name="Test",
        last_name="passenger",
    )


def sample_order(user=None, flight=None, index=0):
    if user is None:
        user = User.objects.create_user(
            username=f"Sample User-{index}",
            password='<PASSWORD>'
        )
    if flight is None:
        flight = sample_flight()
    order = Order.objects.create(
        user=user,
    )
    passenger1 = sample_passenger()
    passenger2 = sample_passenger()
    Ticket.objects.create(
        row=1, seat=1, flight=flight,
        order=order, passenger=passenger1,
    )
    Ticket.objects.create(
        row=1, seat=2, flight=flight,
        order=order, passenger=passenger2,
    )
    return order


class AuthenticatedUserApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        for i in range(9):
            sample_order(index=i)

        self.sample_order = Order.objects.first()

        self.user = User.objects.create_user(
            username='Test-user',
            password='<PASSWORD>'
        )

        self.data = {

            "tickets": [
                {
                    "row": 2,
                    "seat": 1,
                    "flight": 1,
                    "passenger": {
                        "first_name": "test-1",
                        "last_name": "test-1"
                    }
                },
                {
                    "row": 2,
                    "seat": 2,
                    "flight": 1,
                    "passenger": {
                        "first_name": "test-2",
                        "last_name": "test-2"
                    }
                }
            ]

        }

        self.client.force_authenticate(user=self.user)

    def test_get_no_orders(self):
        response = self.client.get(ORDER_URL)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

    def test_get_created_orders(self):
        for _ in range(3):
            sample_order(self.user)
        orders = Order.objects.filter(user=self.user)
        response = self.client.get(ORDER_URL)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)
        self.assertEqual(response.data, OrderListSerializer(orders, many=True).data)

    def test_create_order(self):
        order_count = Order.objects.filter(user=self.user).count()
        response = self.client.post(ORDER_URL, self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            Order.objects.filter(user=self.user).count(),
            order_count + 1
        )
        order = Order.objects.filter(user=self.user).last()
        self.assertEqual(response.data, OrderSerializer(order, many=False).data)

    def test_get_orders_except_someone_orders(self):
        user = User.objects.create_user(
            username='Test-for-Order',
            password='<PASSWORD>'
        )
        order = sample_order(user)
        response = self.client.get(ORDER_URL, self.data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)
        self.assertNotIn(OrderSerializer(order, many=False).data, response.data)

    def test_create_order_with_another_user(self):
        user = User.objects.create_user(
            username='Test-for-Order',
            password='<PASSWORD>'
        )
        self.data["user"] = user.id

        response = self.client.post(ORDER_URL, self.data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(Order.objects.filter(user=user)), 0)
        order = Order.objects.get(pk=response.data["id"])
        self.assertNotEqual(order.user, user)

    def test_create_order_raise_exception(self):
        flight = sample_flight()
        sample_order(flight=flight, index=10)
        order_data = {
            "tickets": [
                {
                    "row": 1,
                    "seat": 1,
                    "flight": flight.id,
                    "passenger": {
                        "first_name": "test-unique",
                        "last_name": "test-unique"
                    }
                }
            ]
        }
        response = self.client.post(ORDER_URL, order_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data["tickets"][0]["non_field_errors"],
            [
                ErrorDetail(
                    string='The fields flight, row, seat must make a unique set.',
                    code='unique'
                )
            ]
        )

    def test_update_order_forbidden(self):
        another_user = User.objects.create_user(
            username="Another User",
            password="PASSWORD"
        )
        order = Order.objects.create(
            user=self.user,
        )
        data = {"user": another_user.id}
        response = self.client.put(f"{ORDER_URL}{order.id}/", data)

        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        order.refresh_from_db()
        self.assertEqual(len(Order.objects.filter(pk=self.user.id)), 1)

    def test_cancel_order(self):
        order = Order.objects.create(
            user=self.user,
        )
        response = self.client.post(f"{ORDER_URL}{order.id}/cancel/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        order.refresh_from_db()
        self.assertTrue(order.is_cancelled)

    def test_delete_order_forbidden(self):
        order = Order.objects.create(
            user=self.user,
        )
        response = self.client.delete(f"{ORDER_URL}{order.id}/")

        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertEqual(len(Order.objects.filter(pk=order.id)), 1)

    def test_get_someone_order(self):
        another_user = User.objects.create_user(
            username="Another User",
            password="PASSWORD"
        )
        order = Order.objects.create(
            user=another_user,
        )
        response = self.client.get(f"{ORDER_URL}{order.id}/")

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data["detail"], "No Order matches the given query.")

    def test_get_invalid_order(self):
        response = self.client.get(f"{ORDER_URL}1001/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class UnauthenticatedUserApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.data = {

            "tickets": [
                {
                    "row": 2,
                    "seat": 1,
                    "flight": 1,
                    "passenger": {
                        "first_name": "test-1",
                        "last_name": "test-1"
                    }
                },
                {
                    "row": 2,
                    "seat": 2,
                    "flight": 1,
                    "passenger": {
                        "first_name": "test-2",
                        "last_name": "test-2"
                    }
                }
            ]

        }

    def test_create_order_forbidden(self):
        response = self.client.post(ORDER_URL, self.data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_order_forbidden(self):
        response = self.client.put(f"{ORDER_URL}1/", self.data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_order_forbidden(self):
        response = self.client.delete(
            f"{ORDER_URL}1/",
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
