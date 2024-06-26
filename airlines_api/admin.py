from django.contrib import admin
from airlines_api.models import (
    Route,
    Passenger,
    AirplaneType,
    Airport,
    Airplane,
    Flight,
    Crew,
    Ticket,
)

admin.site.register(Route)
admin.site.register(Passenger)
admin.site.register(Airport)
admin.site.register(Airplane)
admin.site.register(Flight)
admin.site.register(AirplaneType)
admin.site.register(Crew)
admin.site.register(Ticket)
