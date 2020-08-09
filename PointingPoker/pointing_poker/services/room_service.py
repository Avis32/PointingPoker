from django.db.models import Model, QuerySet

from pointing_poker.models import Room

LOGIN = 'login'
SEND_EVALUATION = 'send_evaluation'


EventInputs = (
    LOGIN,
    SEND_EVALUATION,
)


class RoomConsumerService:
    def __init__(self, room_name):
        self.room_name = room_name
        self.room: QuerySet = Room.objects.filter(room_name=room_name)

    def room_exist(self) -> bool:
        return self.room.exists()

    # def handle_input(self):
