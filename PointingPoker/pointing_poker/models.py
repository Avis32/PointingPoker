from django.db import models

# Create your models here.


class Room(models.Model):
    room_name = models.CharField(max_length=128)
    password = models.CharField(max_length=128)


class Ticket(models.Model):
    title = models.CharField(max_length=128, blank=True)
    evaluation = models.PositiveSmallIntegerField
    room = models.ForeignKey('Room', on_delete=models.CASCADE, related_name='tickets')

