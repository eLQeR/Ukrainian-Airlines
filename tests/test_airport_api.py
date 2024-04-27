from django.core.exceptions import ObjectDoesNotExist
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from airlines_api.models import Airport, Route
from airlines_api.serializers import AirportSerializer, AirportDetailSerializer
from user.models import User


class UserApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        user = User.objects.create_user(username='user', password='<PASSWORD>')
        self.client.force_authenticate(user=user)
        self.data = {
                "name": "Scarlett",
                "closest_big_city": "New York",
            }

        Airport.objects.create(name="Georginia", closest_big_city="Milan")
        self.airport = Airport.objects.create(name="Kean", closest_big_city="Paris")

    def test_get_airports(self):
        response = self.client.get("/api/airlines/airports/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        actors_full_names = [
            airport["name"] + " - " + airport["closest_big_city"]
            for airport in response.data
            ]
        self.assertEqual(
            actors_full_names, ["Georginia - Milan", "Kean - Paris"]
        )

    def test_filtered_airports(self):
        Airport.objects.create(name="Lasam", closest_big_city="Leon")

        response = self.client.get("/api/airlines/airports/?city=paris&name=kean")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data),  1)

        self.assertEqual(response.data, AirportSerializer([self.airport], many=True).data)

    def test_retrieve_airport(self):
        airport2 = Airport.objects.create(name="Lasam", closest_big_city="Leon")
        Route.objects.create(source=self.airport, destination=airport2, distance=100)
        response = self.client.get("/api/airlines/airports/2/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        airport = Airport.objects.get(pk=2)
        self.assertEqual(response.data, AirportDetailSerializer(airport, many=False).data)

    def test_create_airport_forbidden(self):
        response = self.client.post(
            "/api/airlines/airports/",
            self.data,
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertRaises(ObjectDoesNotExist, Airport.objects.get, name="Scarlett")

    def test_update_airport_forbidden(self):
        response = self.client.put(
            "/api/airlines/airports/1/",
            self.data,
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertRaises(ObjectDoesNotExist, Airport.objects.get, name="Scarlett")

    def test_delete_airport_forbidden(self):
        response = self.client.delete(
            "/api/airlines/airports/1/",
        )
        db_airport_id_1 = Airport.objects.filter(pk=1)

        self.assertEqual(db_airport_id_1.count(), 1)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_invalid_airport(self):
        response = self.client.get("/api/airlines/airports/1001/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class AdminApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        user = User.objects.create_superuser(username='admin_user', password='<PASSWORD>')
        self.client.force_authenticate(user=user)
        self.data = {
                "name": "Scarlett",
                "closest_big_city": "New York",
            }

        Airport.objects.create(name="Georginia", closest_big_city="Milan")
        self.airport = Airport.objects.create(name="Kean", closest_big_city="Paris")

    def test_create_airport(self):
        response = self.client.post(
            "/api/airlines/airports/",
            self.data,
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["closest_big_city"], "New York")
        self.assertEqual(Airport.objects.count(), 3)

    def test_update_airport(self):
        response = self.client.put(
            "/api/airlines/airports/1/",
            self.data,
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["closest_big_city"], "New York")
        self.assertEqual(Airport.objects.count(), 2)
        self.assertEqual(Airport.objects.get(pk=1).name, "Scarlett")


    def test_delete_airport(self):
        response = self.client.delete(
            "/api/airlines/airports/1/",
        )
        db_airport_id_1 = Airport.objects.filter(pk=1)

        self.assertEqual(db_airport_id_1.count(), 0)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_invalid_airport(self):
        response = self.client.delete(
            "/api/airlines/airports/1001/",
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

