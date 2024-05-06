from django.urls import path, include
from rest_framework import routers

from airlines_api.views import (
    OrderViewSet,
    AirportViewSet,
    AirplaneViewSet,
    RouteViewSet,
    FlightViewSet,
    TicketViewSet,
    get_transfer_ways,
)

router = routers.DefaultRouter()
router.register("orders", OrderViewSet)
router.register("flights", FlightViewSet)
router.register("routes", RouteViewSet)
router.register("airports", AirportViewSet)
router.register("airplanes", AirplaneViewSet)
router.register("tickets", TicketViewSet)


urlpatterns = [
    path("", include(router.urls)),
    path("get-ways/", get_transfer_ways, name="get-trasfer-ways"),
]

app_name = "api_airlines"
