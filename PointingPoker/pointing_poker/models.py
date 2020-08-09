from django.db import models

# Create your models here.


class Room(models.Model):
    room_name = models.CharField(max_length=128)


class Ticket(models.Model):
    pass
