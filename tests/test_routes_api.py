from django.core.exceptions import ObjectDoesNotExist
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from airlines_api.models import Airport, Route
from airlines_api.serializers import (
    RouteListSerializer,
    RouteDetailSerializer,
    RouteSerializer,
)
from user.models import User
from django.db.utils import IntegrityError

ROUTE_URL = "/api/airlines/routes/"


class AuthenticatedUserApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        user = User.objects.create_user(username='user', password='<PASSWORD>')
        self.client.force_authenticate(user=user)
        self.data = {
            "source": 5,
            "destination": 1,
        }

        for i in range(1, 5):
            Airport.objects.create(
                name=f"Airport-{i}",
                closest_big_city=f"City-{i}",
            )
        self.airport1 = Airport.objects.first()
        self.airport2 = Airport.objects.last()
        self.route1 = Route.objects.create(source=self.airport1, destination=self.airport2, distance=100)
        self.airport3 = Airport.objects.create(name="Kean", closest_big_city="Paris")
        self.route2 = Route.objects.create(source=self.airport1, destination=self.airport3, distance=100)

    def test_get_routes(self):
        response = self.client.get(ROUTE_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        routes = Route.objects.all()
        self.assertEqual(
            response.data, RouteListSerializer(routes, many=True).data
        )

    def test_filtered_routes_by_source(self):
        airport_with_no_routes = Airport.objects.create(name="Lasam", closest_big_city="Leon")

        response = self.client.get(f"{ROUTE_URL}?source_id=1")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data, RouteListSerializer(Route.objects.filter(source_id=1), many=True).data)
        response = self.client.get(f"{ROUTE_URL}?source_id={airport_with_no_routes.id}")
        self.assertEqual(len(response.data), 0)

    def test_filtered_routes_by_destination(self):
        airport_with_no_routes = Airport.objects.create(name="Lasam", closest_big_city="Leon")

        response = self.client.get(f"{ROUTE_URL}?destination_id=4")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data, RouteListSerializer(Route.objects.filter(destination_id=4), many=True).data)
        response = self.client.get(f"{ROUTE_URL}?destination_id={airport_with_no_routes.id}")
        self.assertEqual(len(response.data), 0)

    def test_get_route(self):
        response = self.client.get(f"{ROUTE_URL}1/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, RouteDetailSerializer(self.route1, many=False).data)

    def test_get_invalid_route(self):
        response = self.client.get(f"{ROUTE_URL}1001/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_create_route_forbidden(self):
        response = self.client.post(
            "/api/airlines/routes/",
            {
                "source": 5,
                "destination": 1,
            },
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertRaises(ObjectDoesNotExist, Route.objects.get, source=5)

    def test_update_route_forbidden(self):
        response = self.client.put(
            f"{ROUTE_URL}1/",
            {
                "source": 5,
                "destination": 1,
            },
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertRaises(ObjectDoesNotExist, Route.objects.get, source=5)

    def test_delete_route_forbidden(self):
        response = self.client.delete(
            f"{ROUTE_URL}1/",
        )
        db_route_id_1 = Route.objects.filter(pk=1)

        self.assertEqual(db_route_id_1.count(), 1)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class UnauthenticatedUserApiTests(AuthenticatedUserApiTests):
    def setUp(self):
        super().setUp()
        self.client.logout()

    def test_create_route_forbidden(self):
        response = self.client.post(ROUTE_URL, self.data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_route_forbidden(self):
        response = self.client.put(f"{ROUTE_URL}1/", self.data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_route_forbidden(self):
        response = self.client.delete(
            f"{ROUTE_URL}1/",
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class AdminApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        user = User.objects.create_superuser(username='admin_user', password='<PASSWORD>')
        self.client.force_authenticate(user=user)
        self.data = {
            "source": 1,
            "destination": 3,
            "distance": 100
        }

        self.airport1 = Airport.objects.create(
            name=f"Airport-1",
            closest_big_city=f"City-1",
        )
        self.airport2 = Airport.objects.create(
            name=f"Airport-2",
            closest_big_city=f"City-2",
        )
        self.route = Route.objects.create(source=self.airport1, destination=self.airport2, distance=100)
        self.airport3 = Airport.objects.create(name="Kean", closest_big_city="Paris")

    def test_create_airport(self):
        count_routes = Route.objects.count()
        response = self.client.post(
            ROUTE_URL,
            self.data,
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data, RouteSerializer(Route.objects.last(), many=False).data)
        self.assertEqual(Route.objects.count(), count_routes + 1)

    def test_create_routes_raise_exception(self):
        self.data.update({"destination": 2})
        response = self.client.post(
            ROUTE_URL,
            self.data,
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["non_field_errors"], [
            "The fields source, destination must make a unique set."
        ])
        kwargs = {
            "source": self.airport1,
            "destination": self.airport2,
            "distance": 100
        }
        self.assertRaises(
            IntegrityError,
            Route.objects.create,
            **kwargs
        )

    def test_update_route(self):
        self.data.update({"destination": self.airport3.id})
        response = self.client.put(
            f"{ROUTE_URL}1/",
            self.data,
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["destination"], 3)
        self.assertEqual(Route.objects.get(pk=1).destination, self.airport3)

    def test_delete_route(self):
        response = self.client.delete(
            f"{ROUTE_URL}1/",
        )
        db_route_id_1 = Route.objects.filter(pk=1)

        self.assertEqual(db_route_id_1.count(), 0)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_invalid_route(self):
        response = self.client.delete(
            f"{ROUTE_URL}1001/",
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
