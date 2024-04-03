from django.contrib.auth import get_user_model
from django.db import models


class Airport(models.Model):
    name = models.CharField(max_length=255)
    closest_big_city = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.name} - {self.closest_big_city}"


class Route(models.Model):
    source = models.ForeignKey(to=Airport, on_delete=models.CASCADE, related_name="routes_as_sourse")
    destination = models.ForeignKey(to=Airport, on_delete=models.CASCADE, related_name="routes_as_destination")
    distance = models.FloatField()

    def __str__(self):
        return f"{self.source} -> {self.destination}"


class AirplaneType(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Airplane(models.Model):
    name = models.CharField(max_length=255)
    rows = models.IntegerField()
    seats_in_row = models.IntegerField()
    airplane_type = models.ForeignKey(to=AirplaneType, on_delete=models.CASCADE, related_name="airplanes")

    def __str__(self):
        return self.name


class Crew(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Flight(models.Model):
    route = models.ForeignKey(to=Route, on_delete=models.CASCADE, related_name="flights")
    airplane = models.ForeignKey(to=Airplane, on_delete=models.CASCADE, related_name="flights")
    arrival_time = models.DateTimeField()
    departure_time = models.DateTimeField()
    crews = models.ManyToManyField(to=Crew, blank=True)


class Passenger(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    flight = models.ForeignKey(to=Flight, on_delete=models.CASCADE, related_name="passengers")


class Order(models.Model):
    created_at = models.DateTimeField(auto_created=True, auto_now_add=True)
    user = models.ForeignKey(to=get_user_model(), on_delete=models.DO_NOTHING, related_name="orders")

    def __str__(self):
        return f"{self.created_at} - {self.user}"


class Ticket(models.Model):
    row = models.IntegerField()
    seat = models.IntegerField()
    flight = models.ForeignKey(to=Flight, on_delete=models.DO_NOTHING, related_name="tickets")
    order = models.ForeignKey(to=Order, on_delete=models.CASCADE, related_name="tickets")
    passenger = models.OneToOneField(to=Passenger, on_delete=models.CASCADE, related_name="ticket")

    def __str__(self):
        return f"{self.row} - {self.seat} - {self.passenger}"