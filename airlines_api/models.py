import uuid
import os

from django.contrib.auth import get_user_model
from django.db import models
from django.utils.text import slugify
from rest_framework.exceptions import ValidationError


class Airport(models.Model):
    name = models.CharField(max_length=255)
    closest_big_city = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.name} - {self.closest_big_city}"

    class Meta:
        ordering = ["name"]


class Route(models.Model):
    source = models.ForeignKey(
        to=Airport,
        on_delete=models.CASCADE,
        related_name="routes_as_sourse"
    )
    destination = models.ForeignKey(
        to=Airport,
        on_delete=models.CASCADE,
        related_name="routes_as_destination"
    )
    distance = models.FloatField()

    def __str__(self):
        return f"{self.source} -> {self.destination}"

    class Meta:
        unique_together = ("source", "destination")


class AirplaneType(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["name"]


def create_airplane_image_path(instance, filename):
    _, extension = os.path.splitext(filename)
    return os.path.join(
        "planes/", f"{slugify(instance.name)}-{uuid.uuid4()}{extension}"
    )


class Airplane(models.Model):
    name = models.CharField(max_length=255)
    rows = models.IntegerField()
    seats_in_row = models.IntegerField()
    airplane_type = models.ForeignKey(
        to=AirplaneType, on_delete=models.CASCADE, related_name="airplanes"
    )
    image = models.ImageField(
        upload_to=create_airplane_image_path,
        default="planes/no_plan_photo.png"
    )

    def __str__(self):
        return self.name

    @property
    def capacity(self) -> int:
        return self.rows * self.seats_in_row

    class Meta:
        ordering = ["name"]


def create_avatar_path(instance, filename):
    _, extension = os.path.splitext(filename)
    return os.path.join(
        "avatars/", f"{slugify(instance.last_name)}-{uuid.uuid4()}{extension}"
    )


class Crew(models.Model):
    avatar = models.ImageField(
        upload_to=create_avatar_path, default="avatars/no_avatar.jpg"
    )
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    class Meta:
        ordering = ["last_name"]


class Flight(models.Model):
    route = models.ForeignKey(
        to=Route, on_delete=models.CASCADE, related_name="flights"
    )
    airplane = models.ForeignKey(
        to=Airplane, on_delete=models.CASCADE, related_name="flights"
    )
    departure_time = models.DateTimeField()
    arrival_time = models.DateTimeField()
    crews = models.ManyToManyField(to=Crew, blank=True)
    is_completed = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.route} ({self.departure_time})"

    @property
    def capacity(self):
        return self.airplane.capacity

    @property
    def time_of_flight(self):
        return str(self.arrival_time - self.departure_time)

    class Meta:
        ordering = ["departure_time"]


class Passenger(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)

    class Meta:
        ordering = ["last_name"]


class Order(models.Model):
    created_at = models.DateTimeField(auto_created=True, auto_now_add=True)
    user = models.ForeignKey(
        to=get_user_model(), on_delete=models.DO_NOTHING, related_name="orders"
    )
    is_cancelled = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.created_at} - {self.user}"

    class Meta:
        ordering = ["-created_at"]


class Ticket(models.Model):
    row = models.IntegerField()
    seat = models.IntegerField()
    flight = models.ForeignKey(
        to=Flight, on_delete=models.DO_NOTHING, related_name="tickets"
    )
    order = models.ForeignKey(
        to=Order, on_delete=models.CASCADE, related_name="tickets"
    )
    passenger = models.OneToOneField(
        to=Passenger, on_delete=models.CASCADE, related_name="ticket"
    )

    class Meta:
        unique_together = ("flight", "row", "seat")
        ordering = ("row", "seat")

    def __str__(self):
        return f"{self.flight} {self.row} - {self.seat} - {self.passenger}"

    @staticmethod
    def validate_ticket(row, seat, airplane, error_to_raize):
        for ticket_attr_value, ticket_attr_name, airplane_attr_name in [
            (row, "row", "rows"),
            (seat, "seat", "seats_in_row"),
        ]:
            count_attr_value = getattr(airplane, airplane_attr_name)
            if not (1 <= ticket_attr_value <= count_attr_value):
                raise error_to_raize(
                    {
                        ticket_attr_name: f"{ticket_attr_name} "
                        f"number must be in available range: "
                        f"(1, {airplane_attr_name}): "
                        f"(1, {count_attr_value})"
                    }
                )

    def clean(self):
        Ticket.validate_ticket(
            self.row,
            self.seat,
            self.flight.airplane,
            ValidationError
        )

    def save(
        self,
        force_insert=False,
        force_update=False,
        using=None,
        update_fields=None,
    ):
        self.full_clean()
        return super(Ticket, self).save(
            force_insert, force_update, using, update_fields
        )
