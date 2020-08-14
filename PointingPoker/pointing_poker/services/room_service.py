from django.db.models import Model, QuerySet
from rest_framework import serializers

from pointing_poker.models import Room

LOGIN = 'login'
SEND_EVALUATION = 'send_evaluation'


EventInputs = (
    LOGIN,
    SEND_EVALUATION,
)


class RoomInputSerializer(serializers.Serializer):
    event = serializers.ChoiceField(choices=EventInputs)
    content = serializers.CharField


class RoomConsumerService:
    @staticmethod
    def room_exist(room_name: str) -> bool:
        room: QuerySet = Room.objects.filter(room_name=room_name)
        return room.exists()

    @staticmethod
    def login(room_name, password) -> bool:
        """
        :param room_name:
        :param password:
        :return bool: is password correct
        """
        room: Room = Room.objects.get(room_name=room_name)
        return room.password == password


    @staticmethod
    def handle_input(data):
        serializer = RoomInputSerializer
        serializer(data).is_valid()
        data = serializer.validated_data
