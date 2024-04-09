
from django.urls import path, include
from rest_framework import routers

from airlines_api.views import (
    OrderViewSet,
    AirportViewSet,
    AirplaneViewSet,
    RouteViewSet,
    FlightViewSet,
    TicketViewSet,
    index,
    WaysToAirportView,
)

router = routers.DefaultRouter()
router.register("orders", OrderViewSet)
router.register("flights", FlightViewSet)
router.register("routes", RouteViewSet)
router.register("airports", AirportViewSet)
router.register("airplanes", AirplaneViewSet)
router.register("tickets", TicketViewSet)


urlpatterns = [
    path('', include(router.urls)),
    path("index/", index, name="index"),
    path("get_ways/", WaysToAirportView.as_view(), name="get_ways"),
]

app_name = "api_airlines"
