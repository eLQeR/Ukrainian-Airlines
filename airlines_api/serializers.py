from django.contrib.auth import get_user_model
from rest_framework import mixins, generics, serializers

from airlines_api.models import (
    Crew,
    Airport,
    Route,
    AirplaneType,
    Airplane,
    Flight,
    Order,
    Ticket,
)


class CrewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Crew
        fields = ("id", "first_name", "last_name")


class AirportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Airport
        fields = ("id", "name", "closest_big_city")


class RouteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Route
        fields = ("id", "source", "destination", "distance")


class AirplaneTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = AirplaneType
        fields = ("id", "name",)


class AirplaneSerializer(serializers.ModelSerializer):
    class Meta:
        model = Airplane
        fields = ("id", "name", "rows", "seats_in_row", "airplane_type")


class FlightSerializer(serializers.ModelSerializer):
    class Meta:
        model = Flight
        fields = ("id", "route", "airplane", "arrival_time", "departure_time")


class TicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = ("id", "row", "seat", "flight", "order")


class OrderSerializer(serializers.ModelSerializer):
    tickets = TicketSerializer(many=True, read_only=False)

    class Meta:
        model = Order
        fields = ("id", "created_at", "user", "tickets")


class TicketDetailSerializer(TicketSerializer):
    order = OrderSerializer(many=False, read_only=True)


class RouteListSerializer(RouteSerializer):
    source = AirportSerializer(read_only=True, many=False)
    destination = AirportSerializer(read_only=True, many=False)


class FlightListSerializer(FlightSerializer):
    route = RouteListSerializer(many=False, read_only= True)
    airplane = serializers.CharField(source="airplane.name", read_only=True)

    class Meta:
        model = Flight
        fields = ("id", "route", "airplane", "arrival_time", "departure_time")


class RouteDetailSerializer(RouteListSerializer):
    flights = FlightListSerializer(many=True, read_only=True)

    class Meta:
        model = Route
        fields = ("id", "source", "destination", "distance", "flights")

