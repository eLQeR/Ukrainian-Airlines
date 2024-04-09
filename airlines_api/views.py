import datetime

from django.db.models import Count, F
from django.http import HttpResponse, Http404
from rest_framework import mixins, viewsets, generics
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from airlines_api.permissions import IsAdminOrIfAuthenticatedReadOnly
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
    TicketListSerializer
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
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)


class AirplaneViewSet(
    viewsets.ModelViewSet
):
    queryset = Airplane.objects.all()
    serializer_class = AirplaneSerializer
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)

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
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)

    def get_serializer_class(self):
        if self.action == 'list':
            return FlightListSerializer
        if self.action == 'retrieve':
            return FlightDetailSerializer
        return FlightSerializer

    def get_queryset(self):
        queryset = self.queryset
        departure_time = self.request.query_params.get("departure_time", None)
        route_id = self.request.query_params.get("route_id", None)
        if route_id:
            queryset = queryset.filter(route_id=route_id)
        if departure_time:
            queryset = queryset.filter(departure_time=departure_time)

        if self.action in ('list', "retrieve"):
            queryset = queryset.select_related(
            ).annotate(tickets_avaliable=(F("airplane__rows") * F("airplane__seats_in_row")) - Count('tickets'))
        return queryset


class RouteViewSet(
    viewsets.ModelViewSet
):
    queryset = Route.objects.all()
    serializer_class = RouteSerializer
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)

    def get_serializer_class(self):
        if self.action == "create":
            return RouteSerializer
        if self.action == "retrieve":
            return RouteDetailSerializer
        return RouteListSerializer

    def get_queryset(self):
        queryset = self.queryset
        destination_id = self.request.query_params.get("destination_id", None)
        source_id = self.request.query_params.get("source_id", None)
        if source_id:
            queryset = queryset.filter(source_id=source_id)
        if destination_id:
            queryset = queryset.filter(departure_time=destination_id)
        return queryset


class TicketViewSet(
    viewsets.ModelViewSet
):
    queryset = Ticket.objects.all()
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAdminUser,)

    def get_serializer_class(self):
        #TODO custom action to get all passenger from flight
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


def index(request):
    airport1 = Airport.objects.first()
    airport2 = Airport.objects.last()
    return HttpResponse(str(get_ways_to_airport(airport1, airport2, "2021-02-01")))


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
class WaysToAirportView(generics.ListAPIView):
    queryset = Flight.objects.all()
    def get_queryset(self):
        airport1 = self.request.query_params.get("airport1", None)
        airport2 = self.request.query_params.get("airport2", None)
        date = self.request.query_params.get("date", None)
        if not(airport1 and airport2 and date):
            return Http404("Please enter both airports!")
        airport1 = get_object_or_404(Airport, pk=airport1)
        airport2 = get_object_or_404(Airport, pk=airport2)

        print("source ", airport1)
        print("destination ", airport2)
        right_ways = Flight.objects.filter(route__destination=airport1, route__source=airport2, departure_time__gt=date)
        if right_ways:
            return right_ways

        return get_transfer_flights(airport1, airport2, date)

    def get_serializer_class(self):
        return FlightDetailSerializer



def get_ways_to_airport(airport1: Airport, airport2: Airport, date: str):
    print("source ", airport1)
    print("destination ", airport2)
    right_ways = Flight.objects.filter(route__destination=airport1, route__source=airport2, departure_time__gt=date)
    if right_ways:
        return right_ways
    results = {
        "result": f"There are no right flight from {airport1.name} to {airport2.name}.",
        "not_right_flights": get_transfer_flights(airport1, airport2, date)
    }
    if right_ways.get("not_right_flights"):
        "first_flight"
    print("result")
    print(results)
    return results


def get_transfer_flights(airport1: Airport, airport2: Airport, date: str):
    transfer_flights = []
    flights_avaliable = Flight.objects.filter(
        departure_time__gt=date,
        departure_time__day=date[-1]
    )
    print("flights_avaliable ", flights_avaliable)

    airports_as_transfer = [
        route.source
        for route in Route.objects.filter(
            destination=airport2
        ).order_by('distance')
    ]

    print("airports_as_transfer", airports_as_transfer)

    for airport in airports_as_transfer:
        flights = flights_avaliable.filter(route__source=airport, route__destination=airport2)
        if flights:
            # not_right_flights[airport.name] = [str(flight) for flight in flights]
            transfer_flights.extend(flights)

    print(transfer_flights)
    if not transfer_flights:
        return None

    return transfer_flights

