from django.contrib.auth import get_user_model
from django.db import transaction
from rest_framework import mixins, generics, serializers
from rest_framework.exceptions import ValidationError

from airlines_api.models import (
    Crew,
    Airport,
    Route,
    AirplaneType,
    Airplane,
    Flight,
    Order,
    Ticket,
    Passenger,
)


class CrewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Crew
        fields = ("id", "first_name", "last_name", "avatar")


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
        fields = ("id", "name", "rows", "seats_in_row", "airplane_type", "image")


class AirplaneFlightSerializer(serializers.ModelSerializer):
    class Meta:
        model = Airplane
        fields = ("name", "image")


class AirplaneDetailSerializer(serializers.ModelSerializer):
    airplane_type = serializers.CharField(source="airplane_type.name", read_only=True)

    class Meta:
        model = Airplane
        fields = ("id", "name", "rows", "seats_in_row", "capacity", "airplane_type", "image")


class FlightSerializer(serializers.ModelSerializer):
    class Meta:
        model = Flight
        fields = ("id", "route", "airplane", "arrival_time", "departure_time", "crews")


class PassengerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Passenger
        fields = ("id", "first_name", "last_name")


class TicketSerializer(serializers.ModelSerializer):
    passenger = PassengerSerializer(many=False, read_only=False)

    class Meta:
        model = Ticket
        fields = ("id", "row", "seat", "flight", "passenger")

    def validate(self, attrs):
        data = super(TicketSerializer, self).validate(attrs=attrs)
        Ticket.validate_ticket(
            attrs["row"],
            attrs["seat"],
            attrs["flight"].airplane,
            ValidationError
        )
        return data


class FlightTicketSerializer(serializers.ModelSerializer):
    route = RouteSerializer(many=False, read_only=True)

    class Meta:
        model = Flight
        fields = ("id", "route")


class OrderSerializer(serializers.ModelSerializer):
    tickets = TicketSerializer(many=True, read_only=False, allow_empty=True)

    class Meta:
        model = Order
        fields = ("id", "created_at", "tickets")

    def create(self, validated_data):
        with transaction.atomic():
            tickets_data = validated_data.pop("tickets")
            order = Order.objects.create(**validated_data)
            for ticket_data in tickets_data:
                passanger = Passenger.objects.create(
                    **ticket_data.pop("passenger")
                )
                Ticket.objects.create(passenger=passanger, order=order, **ticket_data)
            return order


class RouteListSerializer(RouteSerializer):
    source = AirportSerializer(read_only=True, many=False)
    destination = AirportSerializer(read_only=True, many=False)


class RouteFlightSerializer(serializers.ModelSerializer):
    source = serializers.CharField(source="source.closest_big_city", read_only=True)
    destination = serializers.CharField(source="destination.closest_big_city", read_only=True)

    class Meta:
        model = Route
        fields = ("source", "destination", "distance")


class FlightListSerializer(FlightSerializer):
    route = RouteFlightSerializer(many=False, read_only=True)
    airplane = serializers.SlugRelatedField(slug_field="name", read_only=True)
    capacity = serializers.IntegerField(source="airplane.capacity", read_only=True)
    tickets_avaliable = serializers.IntegerField(read_only=True)

    class Meta:
        model = Flight
        fields = (
            "id", "arrival_time", "departure_time",
            "time_of_flight", "route", "airplane",
            "capacity", "tickets_avaliable"
        )


class TicketFlightSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = ("row", "seat")


class TicketListSerializer(serializers.ModelSerializer):
    passenger = PassengerSerializer(many=False, read_only=True)

    class Meta:
        model = Ticket
        fields = ("id", "row", "seat", "passenger")


class FlightDetailSerializer(serializers.ModelSerializer):
    airplane = AirplaneDetailSerializer(many=False, read_only=True)
    crews = CrewSerializer(many=True, read_only=True)
    route = RouteListSerializer(many=False, read_only=True)
    tickets_taken = TicketFlightSerializer(source="tickets", many=True, read_only=True)
    tickets_avaliable = serializers.IntegerField(read_only=True)

    class Meta:
        model = Flight
        fields = (
            "id", "arrival_time", "departure_time",
            "time_of_flight", "tickets_avaliable", "route",
            "airplane", "crews", "tickets_taken"

        )


class FlightAdminDetailSerializer(FlightDetailSerializer):
    tickets = TicketSerializer(many=True, read_only=True)
    class Meta:
        model = Flight
        fields = (
            "id", "arrival_time", "departure_time",
            "route", "airplane", "crews", "tickets",
        )


class FlightRouteListSerializer(FlightSerializer):
    airplane = serializers.CharField(source="airplane.name", read_only=True)

    class Meta:
        model = Flight
        fields = ("id", "arrival_time", "departure_time", "airplane")


class RouteDetailSerializer(RouteListSerializer):
    flights = FlightRouteListSerializer(many=True, read_only=True)

    class Meta:
        model = Route
        fields = ("id", "source", "destination", "distance", "flights")


class RouteAirportsSerializer(RouteListSerializer):
    class Meta:
        model = Route
        fields = ("id", "source", "destination", "distance")


class AirportDetailSerializer(serializers.ModelSerializer):
    routes_as_sourse = RouteAirportsSerializer(many=True, read_only=True)
    routes_as_destination = RouteAirportsSerializer(many=True, read_only=True)

    class Meta:
        model = Airport
        fields = ("id", "name", "closest_big_city", "routes_as_sourse", "routes_as_destination")
