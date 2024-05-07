import datetime

from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Count, F
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import (
    OpenApiExample,
    OpenApiParameter,
    extend_schema,
    extend_schema_view,
)
from rest_framework import mixins, viewsets, status
from rest_framework.decorators import (
    api_view,
    throttle_classes,
    action
)
from rest_framework.exceptions import ValidationError
from rest_framework.generics import get_object_or_404
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.throttling import UserRateThrottle

from airlines_api.permissions import IsAdminOrReadOnly
from rest_framework_simplejwt.authentication import JWTAuthentication

from airlines_api.models import (
    Order,
    Airport,
    Airplane,
    Ticket,
    Flight,
    Route,
)
from airlines_api.serializers import (
    OrderSerializer,
    AirportSerializer,
    TicketSerializer,
    RouteSerializer,
    AirplaneSerializer,
    FlightSerializer,
    RouteDetailSerializer,
    RouteListSerializer,
    FlightListSerializer,
    AirplaneDetailSerializer,
    FlightDetailSerializer,
    TicketListSerializer,
    PassengerSerializer,
    AirportDetailSerializer,
    FlightAdminDetailSerializer,
    OrderDetailSerializer,
    OrderListSerializer,
)


class MediumResultsSetPagination(PageNumberPagination):
    page_size = 15
    page_size_query_param = "page_size"
    max_page_size = 15


@extend_schema_view(
    list=extend_schema(
        summary="Get list of your orders",
        description="User can get a list of his orders.",
    ),
    retrieve=extend_schema(
        summary="Get a certain order",
        description="User can get a certain his order.",
    ),
    create=extend_schema(
        summary="Get a certain order",
        description="User can create an order.",
    ),
    cancel_order=extend_schema(
        summary="Cancel a certain order",
        description="User can cancel a certain his order.",
        methods=["POST"],
    ),
)
class OrderViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    pagination_class = MediumResultsSetPagination

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).prefetch_related(
            "tickets__passenger", "tickets__flight"
        )

    def get_serializer_class(self):
        if self.action == "list":
            return OrderListSerializer
        if self.action == "retrieve":
            return OrderDetailSerializer
        return OrderSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=["POST"], url_path="cancel")
    def cancel_order(self, request, pk=None):
        order = self.get_object()
        order.is_cancelled = True
        order.save()
        return Response(
            self.get_serializer(order, many=False).data,
            status=status.HTTP_200_OK
        )


@extend_schema_view(
    update=extend_schema(
        summary="Update a certain airport",
        description="Admin can update a certain airport.",
    ),
    partial_update=extend_schema(
        summary="Partial update a certain airport",
        description="Admin can make partial update a certain airport.",
    ),
    retrieve=extend_schema(
        summary="Get a certain airport",
        description="User can get a certain airport.",
    ),
    create=extend_schema(
        summary="Create an airport",
        description="Admin can create an airport.",
    ),
    destroy=extend_schema(
        summary="Delete a certain airport",
        description="Admin can delete an airport.",
    ),
)
class AirportViewSet(viewsets.ModelViewSet):
    queryset = Airport.objects.all()
    serializer_class = AirportSerializer
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAdminOrReadOnly,)
    pagination_class = MediumResultsSetPagination

    def get_queryset(self):
        queryset = self.queryset
        name = self.request.query_params.get("name", None)
        city = self.request.query_params.get("city", None)

        if name:
            queryset = queryset.filter(name__icontains=name)
        if city:
            queryset = queryset.filter(closest_big_city__icontains=city)
        if self.action == "retrieve":
            queryset = queryset.prefetch_related(
                "routes_as_sourse__destination",
                "routes_as_destination__source"
            )

        return queryset

    @extend_schema(
        summary="Get list of airports",
        description="User can get a list of airports.",
        methods=["GET"],
        parameters=[
            OpenApiParameter(
                name="name",
                description="Filter by name of airport",
                required=False,
                type=str,
            ),
            OpenApiParameter(
                name="city",
                description="Filter by city name",
                required=False,
                type=str
            ),
        ],
        examples=[
            OpenApiExample(
                "Example 1",
                value={"name": "Sharon", "city": "Paris"}
            )
        ],
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def get_serializer_class(self):
        if self.action == "retrieve":
            return AirportDetailSerializer

        return AirportSerializer


@extend_schema_view(
    list=extend_schema(
        summary="Get list of airplanes",
        description="User can get a list of airplanes.",
        parameters=[
            OpenApiParameter(
                name="airplane_type_id",
                description="Filter by airplane_type id",
                required=False,
                type=int,
            )
        ],
    ),
    update=extend_schema(
        summary="Update a certain airplane",
        description="Admin can update a certain airplane.",
    ),
    partial_update=extend_schema(
        summary="Partial update a certain airplane",
        description="Admin can make partial update a certain airplane.",
    ),
    retrieve=extend_schema(
        summary="Get a certain airplane",
        description="User can get a certain airplane.",
    ),
    create=extend_schema(
        summary="Create an airplane",
        description="Admin can create an airplane.",
    ),
    destroy=extend_schema(
        summary="Delete a certain airplane",
        description="Admin can delete an airplane.",
    ),
)
class AirplaneViewSet(viewsets.ModelViewSet):
    queryset = Airplane.objects.all()
    serializer_class = AirplaneSerializer
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAdminOrReadOnly,)
    pagination_class = MediumResultsSetPagination

    def get_queryset(self):
        queryset = self.queryset
        airplane_type_id = self.request.query_params.get(
            "airplane_type_id", None
        )
        if airplane_type_id:
            queryset = queryset.filter(airplane_type_id=airplane_type_id)
        return queryset.select_related("airplane_type")

    def get_serializer_class(self):
        if self.action == "create":
            return AirplaneSerializer
        return AirplaneDetailSerializer


@extend_schema_view(
    update=extend_schema(
        summary="Update a certain flight",
        description="Admin can update a certain flight.",
    ),
    partial_update=extend_schema(
        summary="Partial update a certain flight",
        description="Admin can make partial update a certain flight.",
    ),
    retrieve=extend_schema(
        summary="Get a certain flight",
        description="User can get a certain flight.",
    ),
    create=extend_schema(
        summary="Create an flight",
        description="Admin can create an flight.",
    ),
    destroy=extend_schema(
        summary="Delete a certain flight",
        description="Admin can delete an flight.",
    ),
)
class FlightViewSet(viewsets.ModelViewSet):
    queryset = Flight.objects.all()
    serializer_class = FlightSerializer
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAdminOrReadOnly,)
    pagination_class = MediumResultsSetPagination

    @extend_schema(
        summary="Get taken tickets of flight",
        description="Get all taken tickets of flight",
        methods=["GET"],
    )
    @action(
        detail=True,
        methods=["GET"],
        url_path="tickets",
        permission_classes=[IsAdminUser],
    )
    def get_tickets(self, request, pk=None):
        flight = self.get_object()
        return Response(
            self.get_serializer(flight.tickets.all(), many=True).data,
            status=status.HTTP_200_OK,
        )

    @extend_schema(
        summary="Get passengers of flight",
        description="Get all passengers of flight",
        methods=["GET"],
    )
    @action(
        detail=True,
        methods=["GET"],
        url_path="passengers",
        permission_classes=[IsAdminUser],
    )
    def get_passengers(self, request, pk=None):
        flight = self.get_object()
        passengers = [ticket.passenger for ticket in flight.tickets.all()]
        return Response(
            self.get_serializer(passengers, many=True).data,
            status=status.HTTP_200_OK
        )

    @extend_schema(
        summary="Get list departured flights",
        description="Admin can get a flight list with departured flights",
        methods=["GET"],
        parameters=[
            OpenApiParameter(
                name="source_airport",
                description="Filter by source airport",
                required=False,
                type=int,
            ),
            OpenApiParameter(
                name="destination_airport",
                description="Filter by destination airport",
                required=False,
                type=int,
            ),
            OpenApiParameter(
                name="departure_date",
                required=False,
                type=OpenApiTypes.DATE,
                location=OpenApiParameter.QUERY,
                description="Filter by departure date",
            ),
        ],
        examples=[
            OpenApiExample(
                "Example 1",
                value={
                    "source_airport": 1,
                    "destination_airport": 3,
                    "date": "2025-04-24",
                    "route": 1,
                },
            ),
            OpenApiExample(
                "Example 2",
                value={
                    "date": "2025-04-24",
                    "route": 1
                }
            ),
        ],
    )
    @action(
        detail=False,
        methods=["GET"],
        url_path="passed",
        permission_classes=[IsAdminUser],
        name="passed",
    )
    def get_passed_flights(self, request):
        flights = self.get_queryset()
        return Response(
            self.get_serializer(flights, many=True).data,
            status=status.HTTP_200_OK
        )

    @extend_schema(
        summary="Get a certain departured flight",
        description="Admin can get a flight that has been departured",
        methods=["GET"],
    )
    @action(
        detail=True,
        methods=["GET"],
        url_path="departured",
        permission_classes=[IsAdminUser],
        name="departured",
    )
    def get_departured_flight(self, request, pk=None):
        flight = get_object_or_404(self.get_queryset(), pk=pk)

        return Response(
            self.get_serializer(flight, many=False).data,
            status=status.HTTP_200_OK
        )

    @extend_schema(
        summary="Get list of flights",
        description="User can get a list of flights.",
        parameters=[
            OpenApiParameter(
                name="source_airport",
                description="Filter by source airport",
                required=False,
                type=int,
            ),
            OpenApiParameter(
                name="destination_airport",
                description="Filter by destination airport",
                required=False,
                type=int,
            ),
            OpenApiParameter(
                name="departure_date",
                required=False,
                type=OpenApiTypes.DATE,
                location=OpenApiParameter.QUERY,
                description="Filter by departure date",
            ),
        ],
        examples=[
            OpenApiExample(
                "Example 1",
                value={
                    "source_airport": 1,
                    "destination_airport": 3,
                    "date": "2025-04-24",
                    "route": 1,
                },
            ),
            OpenApiExample(
                "Example 2",
                value={
                    "date": "2025-04-24",
                    "route": 1
                }
            ),
        ],
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def get_serializer_class(self):
        if self.action in ("list", "get_passed_flights"):
            return FlightListSerializer

        elif self.action == "retrieve":
            return FlightDetailSerializer

        elif self.action == "get_tickets":
            return TicketListSerializer

        elif self.action == "get_departured_flight":
            return FlightAdminDetailSerializer

        elif self.action == "get_passengers":
            return PassengerSerializer

        return FlightSerializer

    def get_queryset(self):
        queryset = self.queryset
        if self.action not in ("get_departured_flight", "get_passed_flights"):
            queryset = queryset.filter(is_completed=False)

        departure_date = self.request.query_params.get(
            "departure_date", None
        )
        route_id = self.request.query_params.get("route", None)
        source_airport_id = self.request.query_params.get(
            "source_airport", None
        )
        destination_airport_id = self.request.query_params.get(
            "destination_airport", None
        )

        if source_airport_id:
            queryset = queryset.filter(route__source_id=source_airport_id)
        if route_id:
            queryset = queryset.filter(route_id=route_id)
        if departure_date:
            queryset = queryset.filter(departure_time__date=departure_date)
        if destination_airport_id:
            queryset = queryset.filter(
                route__destination_id=destination_airport_id
            )

        if self.action in (
            "list",
            "retrieve",
            "get_passed_flights",
            "get_departured_flight",
        ):
            queryset = queryset.select_related().annotate(
                tickets_avaliable=(F("airplane__rows") * F("airplane__seats_in_row"))
                - Count("tickets")
            )
        return queryset.order_by("departure_time")


@extend_schema_view(
    list=extend_schema(
        summary="Get list of routes",
        description="User can get a list of routes.",
        parameters=[
            OpenApiParameter(
                name="source",
                description="Filter by source id",
                required=False,
                type=int,
            ),
            OpenApiParameter(
                name="destination",
                description="Filter by destination id",
                required=False,
                type=int,
            ),
        ],
    ),
    update=extend_schema(
        summary="Update a certain route",
        description="Admin can update a certain route.",
    ),
    partial_update=extend_schema(
        summary="Partial update a certain route",
        description="Admin can make partial update a certain route.",
    ),
    retrieve=extend_schema(
        summary="Get a certain route",
        description="User can get a certain route.",
    ),
    create=extend_schema(
        summary="Create an route",
        description="Admin can create a route.",
    ),
    destroy=extend_schema(
        summary="Delete a certain route",
        description="Admin can delete a route.",
    ),
)
class RouteViewSet(viewsets.ModelViewSet):
    queryset = Route.objects.all()
    serializer_class = RouteSerializer
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAdminOrReadOnly,)
    pagination_class = MediumResultsSetPagination

    def get_serializer_class(self):
        if self.action == "list":
            return RouteListSerializer
        if self.action == "retrieve":
            return RouteDetailSerializer
        return RouteSerializer

    def get_queryset(self):
        queryset = self.queryset
        destination_id = self.request.query_params.get("destination", None)
        source_id = self.request.query_params.get("source", None)
        if source_id:
            queryset = queryset.filter(source_id=source_id)
        if destination_id:
            queryset = queryset.filter(destination_id=destination_id)
        if self.action == "retrieve":
            queryset = queryset.prefetch_related("flights__airplane")

        return queryset.select_related("destination", "source")


@extend_schema_view(
    list=extend_schema(
        summary="Get list of tickets",
        description="Admin have an opportunity to get list of all tickets",
    ),
    update=extend_schema(
        summary="Update a certain ticket",
        description="Admin have an opportunity to update "
        "certain ticket if there is a need for it",
    ),
    partial_update=extend_schema(
        summary="Partial update a certain ticket",
        description="Admin can make partial update a certain ticket"
        "  if there is a need for it.",
    ),
    retrieve=extend_schema(
        summary="Delete a certain ticket",
        description="Admin have an opportunity to "
                    "delete a ticket of someone's",
    ),
    destroy=extend_schema(
        summary="Delete a certain ticket",
        description="Admin can delete a ticket.",
    ),
)
class TicketViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Ticket.objects.all()
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAdminUser,)

    def get_serializer_class(self):
        if self.action == "list":
            return TicketListSerializer
        return TicketSerializer

    def get_queryset(self):
        queryset = self.queryset
        first_name = self.request.query_params.get("first_name", None)
        last_name = self.request.query_params.get("last_name", None)
        flight = self.request.query_params.get("flight", None)
        if first_name:
            queryset = queryset.filter(
                passenger__first_name__icontains=first_name
            )
        if last_name:
            queryset = queryset.filter(
                passenger__last_name__icontains=last_name
            )
        if flight:
            queryset = queryset.filter(flight_id=flight)
        return queryset.select_related("passenger")


def get_validated_data(query_params) -> tuple:
    airport1_id = query_params.get("airport1", None)
    airport2_id = query_params.get("airport2", None)
    date = query_params.get("date", None)
    if not (airport1_id and airport2_id and date):
        raise ValidationError("Please enter both airports and date!!!")
    airport1 = Airport.objects.get(pk=airport1_id)
    airport2 = Airport.objects.get(pk=airport2_id)
    date = datetime.datetime.strptime(
        query_params.get("date", None), "%Y-%m-%d"
    )

    return airport1, airport2, date


class TenPerMinuteUserThrottle(UserRateThrottle):
    rate = "10/minute"


@extend_schema(
    responses={200: FlightListSerializer},
    summary="Get list of right or transfer flights",
    description="User can list of right or transfer "
    "flights from one airport to another.",
    methods=["GET"],
    parameters=[
        OpenApiParameter(
            name="airport1",
            description="Enter a source airport's id",
            required=True,
            type=int,
        ),
        OpenApiParameter(
            name="airport2",
            description="Enter a destination airport's id",
            required=True,
            type=int,
        ),
        OpenApiParameter(
            name="date",
            required=True,
            type=OpenApiTypes.DATE,
            location=OpenApiParameter.QUERY,
            description="Enter a date.",
        ),
    ],
    examples=[
        OpenApiExample(
            "Kharkiv > Warsaw",
            value={"airport1": 13, "airport2": 18, "date": "2025-07-07"},
        ),
        OpenApiExample(
            "Kyiv > New-York",
            value={"airport1": 11, "airport2": 22, "date": "2025-07-07"},
        ),
        OpenApiExample(
            "Kharkiv > Kyiv",
            value={"airport1": 13, "airport2": 11, "date": "2025-07-07"},
        ),
        OpenApiExample(
            "Kyiv > Prague",
            value={"airport1": 11, "airport2": 19, "date": "2025-07-07"},
        ),
    ],
)
@api_view(["GET"])
@throttle_classes([TenPerMinuteUserThrottle])
def get_transfer_ways(request, *args, **kwargs):
    """
    That is  api view to get all available right or transfer
    ways to certain airport and on certain date
    """
    try:
        airport1, airport2, date = get_validated_data(request.query_params)
    except ObjectDoesNotExist:
        return Response(
            {"error": "Please enter correct airport1 and airport2"},
            status=status.HTTP_400_BAD_REQUEST,
        )
    except ValueError as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    return Response(get_ways_to_airport(airport1, airport2, date))


def get_ways_to_airport(airport1: Airport, airport2: Airport, date: datetime):
    """ "The function that tries to find right ways to certain airport,
    otherwise call 'get_transfer_flights' function"""

    right_ways = Flight.objects.filter(
        route__destination=airport2,
        route__source=airport1,
        departure_time__gt=date,
        departure_time__lt=date + datetime.timedelta(days=2),
    )

    if right_ways:
        return {"result": FlightListSerializer(right_ways, many=True).data}

    transfer_flights = get_transfer_flights(airport1, airport2, date)

    if transfer_flights:
        return {
            "result": [
                FlightListSerializer(flights, many=True).data
                for flights in transfer_flights
            ]
        }

    return {
        "result": f"There are no any flight from {airport1.name} "
                  f"to {airport2.name} in {date.strftime('%Y-%m-%d')}"
    }


def get_transfer_flights(airport1: Airport, airport2: Airport, date: str):
    """That is am limited and optimized Dijkstra algorithm to find the shortest
    paths from airport1 to airport2 by only one transfer airport"""
    transfer_flights = []
    flights_avaliable = Flight.objects.filter(
        departure_time__gt=date,
        departure_time__lt=date + datetime.timedelta(days=2),
    )

    routes = Route.objects.filter(destination=airport2).order_by("distance")

    airports_as_transfer = []

    for route in routes:
        if (route.id,) in flights_avaliable.values_list("route"):
            try:
                route_to_transfer = Route.objects.get(
                    source=airport1, destination=route.source
                )
            except ObjectDoesNotExist:
                continue

            if (route_to_transfer.id,) in flights_avaliable.values_list("route"):
                airports_as_transfer.append(
                    (route.source, (flights_avaliable.filter(route=route_to_transfer)))
                )

    for airport, flights in airports_as_transfer:
        destination_flights = flights_avaliable.filter(
            route__source=airport, route__destination=airport2
        )
        if destination_flights:
            for destination_flight in destination_flights:
                for transfer_flight in flights:
                    if transfer_flight.arrival_time < destination_flight.departure_time:
                        transfer_flights.append((transfer_flight, destination_flight))

    if transfer_flights:
        return transfer_flights

    return None
