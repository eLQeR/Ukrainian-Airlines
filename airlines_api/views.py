import datetime

from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Count, F
from rest_framework import mixins, viewsets, generics, status
from rest_framework.decorators import api_view, throttle_classes, action, permission_classes
from rest_framework.exceptions import ValidationError
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework.response import Response
from rest_framework.throttling import UserRateThrottle

from airlines_api.permissions import IsAdminOrReadOnly
from rest_framework_simplejwt.authentication import JWTAuthentication

from airlines_api.models import (
    Order,
    Airport,
    Airplane,
    AirplaneType,
    Passenger,
    Ticket,
    Flight,
    Route,
    Crew
)
from airlines_api.serializers import (
    OrderSerializer,
    AirportSerializer,
    TicketSerializer,
    RouteSerializer,
    AirplaneSerializer,
    AirplaneTypeSerializer,
    FlightSerializer,
    RouteDetailSerializer,
    RouteListSerializer,
    FlightListSerializer,
    AirplaneDetailSerializer,
    FlightDetailSerializer,
    TicketListSerializer,
    PassengerSerializer,
    AirportDetailSerializer,
    FlightAdminDetailSerializer
)


class OrderViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet
):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.action == 'list':
            return OrderSerializer
        return OrderSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class AirportViewSet(
    viewsets.ModelViewSet
):
    queryset = Airport.objects.all()
    serializer_class = AirportSerializer
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAdminOrReadOnly,)

    def get_queryset(self):
        queryset = self.queryset
        name = self.request.query_params.get("name", None)
        city = self.request.query_params.get("city", None)

        if name:
            queryset = queryset.filter(name__icontains=name)
        if city:
            queryset = queryset.filter(closest_big_city__icontains=city)

        return queryset

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return AirportDetailSerializer

        return AirportSerializer


class AirplaneViewSet(
    viewsets.ModelViewSet
):
    queryset = Airplane.objects.all()
    serializer_class = AirplaneSerializer
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAdminOrReadOnly,)

    def get_queryset(self):
        queryset = self.queryset
        airplane_type_id = self.request.query_params.get("airplane_type_id", None)
        if airplane_type_id:
            queryset = queryset.filter(airplane_type_id=airplane_type_id)
        return queryset

    def get_serializer_class(self):
        if self.action == "create":
            return AirplaneSerializer
        return AirplaneDetailSerializer


class FlightViewSet(
    viewsets.ModelViewSet
):
    queryset = Flight.objects.all()
    serializer_class = FlightSerializer
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAdminOrReadOnly,)

    @action(detail=True, methods=['GET'], url_path="tickets", permission_classes=[IsAdminUser])
    def get_tickets(self, request, pk=None):
        flight = self.get_object()
        return Response(self.get_serializer(flight.tickets.all(), many=True).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['GET'], url_path="passengers", permission_classes=[IsAdminUser])
    def get_passengers(self, request, pk=None):
        flight = self.get_object()
        passengers = [ticket.passenger for ticket in flight.tickets.all()]
        return Response(self.get_serializer(passengers, many=True).data, status=status.HTTP_200_OK)

    @action(
        detail=False,
        methods=['GET'],
        url_path="passed",
        permission_classes=[IsAdminUser],
        name='passed'
    )
    def get_passed_flights(self, request):
        flights = self.get_queryset()
        return Response(self.get_serializer(flights, many=True).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['GET'], url_path="departured", permission_classes=[IsAdminUser], name='departured')
    def get_departured_flight(self, request, pk=None):
        flight = get_object_or_404(self.get_queryset(), pk=pk)

        return Response(self.get_serializer(flight, many=False).data, status=status.HTTP_200_OK)

    def get_serializer_class(self):
        if self.action in ('list', "get_passed_flights"):
            return FlightListSerializer

        elif self.action == 'retrieve':
            return FlightDetailSerializer

        elif self.action == 'get_tickets':
            return TicketListSerializer

        elif self.action == 'get_departured_flight':
                return FlightAdminDetailSerializer

        elif self.action == 'get_passengers':
            return PassengerSerializer

        return FlightSerializer

    def get_queryset(self):
        queryset = self.queryset
        if self.action not in ("get_departured_flight", "get_passed_flights"):
            queryset = queryset.filter(is_completed=False)

        departure_date = self.request.query_params.get("departure_date", None)
        route_id = self.request.query_params.get("route", None)
        source_airport_id = self.request.query_params.get("source_airport", None)
        destination_airport_id = self.request.query_params.get("destination_airport", None)

        if source_airport_id:
            queryset = queryset.filter(route__source_id=source_airport_id)
        if destination_airport_id:
            queryset = queryset.filter(route__destination_id=destination_airport_id)
        if route_id:
            queryset = queryset.filter(route_id=route_id)
        if departure_date:
            queryset = queryset.filter(departure_time__date=departure_date)

        if self.action in ('list', "retrieve", "get_passed_flights", "get_departured_flight"):
            queryset = queryset.select_related(
            ).annotate(tickets_avaliable=(F("airplane__rows") * F("airplane__seats_in_row")) - Count('tickets'))
        return queryset


class RouteViewSet(
    viewsets.ModelViewSet
):
    queryset = Route.objects.all()
    serializer_class = RouteSerializer
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAdminOrReadOnly,)

    def get_serializer_class(self):
        if self.action == "list":
            return RouteListSerializer
        if self.action == "retrieve":
            return RouteDetailSerializer
        return RouteSerializer

    def get_queryset(self):
        queryset = self.queryset
        destination_id = self.request.query_params.get("destination_id", None)
        source_id = self.request.query_params.get("source_id", None)
        if source_id:
            queryset = queryset.filter(source_id=source_id)
        if destination_id:
            queryset = queryset.filter(destination_id=destination_id)
        return queryset


class TicketViewSet(
    viewsets.ModelViewSet
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
            queryset = queryset.filter(first_name=first_name)
        if last_name:
            queryset = queryset.filter(last_name=last_name)
        if flight:
            queryset = queryset.filter(flight=flight)
        return queryset


# def index(request, *args, **kwargs):
#     for i in range(1, 10, 2):
#         a1 = Airport.objects.create(name=f"Airport-{i}", closest_big_city=f"City-{i}")
#         a2 = Airport.objects.create(name=f"Airport-{i+1}", closest_big_city=f"City-{i+1}")
#         r1 = Route.objects.create(source=a1, destination=a2, distance=500)
#         r2 = Route.objects.create(source=a2, destination=a1, distance=500)
#         crew1 = Crew.objects.create(first_name=f"Test_{i}", last_name="user")
#         crew2 = Crew.objects.create(first_name=f"Test_{i+1}", last_name="user")
#         airtype = AirplaneType.objects.create(name="Boeing")
#         airplane = Airplane.objects.create(
#             name=f"Boeing-{i}", seats_in_row=10, rows=10, airplane_type=airtype
#         )
#         flight1 = Flight.objects.create(
#             route=r1, airplane=airplane, arrival_time="2021-02-03 19:30", departure_time="2021-02-01 19:30"
#         )
#         flight2 = Flight.objects.create(
#             route=r2, airplane=airplane, arrival_time="2021-02-04 19:30", departure_time="2021-02-03 19:30"
#         )
#         flight1.crews.add(crew1, crew2)
#         flight2.crews.add(crew1, crew2)
#
#


def get_validated_data(query_params) -> tuple:
    airport1_id = query_params.get("airport1", None)
    airport2_id = query_params.get("airport2", None)
    date = query_params.get("date", None)
    if not (airport1_id and airport2_id and date):
        raise ValidationError("Please enter both airports and date!!!")
    airport1 = Airport.objects.get(pk=airport1_id)
    airport2 = Airport.objects.get(pk=airport2_id)
    date = datetime.datetime.strptime(query_params.get("date", None), "%Y-%m-%d")

    return airport1, airport2, date


class FivePerMinuteUserThrottle(UserRateThrottle):
    rate = '10/minute'


@api_view(["GET"])
@throttle_classes([FivePerMinuteUserThrottle])
def get_transfer_ways(request, *args, **kwargs):
    """
    That is  api view to get all available right or transfer
    ways to certain airport and on certain date
    """
    try:
        airport1, airport2, date = get_validated_data(request.query_params)
    except ObjectDoesNotExist:
        return Response({"error": "Please enter correct airport1 and airport2"}, status=status.HTTP_400_BAD_REQUEST)
    except ValueError as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    return Response(get_ways_to_airport(airport1, airport2, date))


def get_ways_to_airport(airport1: Airport, airport2: Airport, date: datetime):

    """"The function that tries to find right ways to certain airport,
    otherwise call 'get_transfer_flights' function """

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
        return {"result": [FlightListSerializer(flights, many=True).data for flights in transfer_flights]}

    return {"result": f"There are no any flight from {airport1.name} to {airport2.name} in {date.strftime('%Y-%m-%d')}"}


def get_transfer_flights(airport1: Airport, airport2: Airport, date: str):
    """That is am limited and optimized Dijkstra algorithm to find the shortest
     paths from airport1 to airport2 by only one transfer airport"""
    transfer_flights = []
    flights_avaliable = Flight.objects.filter(
        departure_time__gt=date,
        departure_time__lt=date + datetime.timedelta(days=2),
    )

    routes = Route.objects.filter(
        destination=airport2
    ).order_by('distance')

    airports_as_transfer = []

    for route in routes:
        if (route.id,) in flights_avaliable.values_list("route"):
            try:
                route_to_transfer = Route.objects.get(source=airport1, destination=route.source)
            except ObjectDoesNotExist:
                continue

            if (route_to_transfer.id,) in flights_avaliable.values_list("route"):
                airports_as_transfer.append((route.source, (flights_avaliable.filter(route=route_to_transfer))))

    for airport, flights in airports_as_transfer:
        destination_flights = flights_avaliable.filter(route__source=airport, route__destination=airport2)
        if destination_flights:
            for destination_flight in destination_flights:
                for transfer_flight in flights:
                    if transfer_flight.arrival_time < destination_flight.departure_time:
                        transfer_flights.append((
                            transfer_flight,
                            destination_flight
                        ))

    if transfer_flights:
        return transfer_flights

    return None
