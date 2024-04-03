from rest_framework import mixins, viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
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
    TicketDetailSerializer,
    RouteSerializer,
    AirplaneSerializer,
    AirplaneTypeSerializer,
    FlightSerializer, RouteDetailSerializer, RouteListSerializer
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


class AirportViewSet(
    viewsets.ModelViewSet
):
    queryset = Airport.objects.all()
    serializer_class = AirportSerializer
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly, )


class AirplaneViewSet(
    viewsets.ModelViewSet
):
    queryset = Airplane.objects.all()
    serializer_class = AirplaneSerializer
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly, )


class FlightViewSet(
    viewsets.ModelViewSet
):
    queryset = Flight.objects.all()
    serializer_class = FlightSerializer
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly, )


class RouteViewSet(
    viewsets.ModelViewSet
):
    queryset = Route.objects.all()
    serializer_class = RouteSerializer
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly, )

    def get_serializer_class(self):
        if self.action == "create":
            return RouteSerializer
        if self.action == "retrieve":
            return RouteDetailSerializer
        return RouteListSerializer


class TicketViewSet(
    viewsets.ModelViewSet
):
    queryset = Ticket.objects.all()
    serializer_class = TicketSerializer
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly, )

#
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
