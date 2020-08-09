import json
from channels.generic.websocket import JsonWebsocketConsumer
from rest_framework import serializers, status

from pointing_poker.services.room_service import RoomConsumerService

LOGIN = 'login'
SEND_EVALUATION = 'send_evaluation'


EventInputs = (
    LOGIN,
    SEND_EVALUATION,
)


class RoomInputSerializer(serializers.Serializer):
    event = serializers.ChoiceField(choices=EventInputs)
    content = serializers.CharField


class RoomConsumer(JsonWebsocketConsumer):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.username: str = ""
        self.room_service: RoomConsumerService = None

    def connect(self):
        room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_service = RoomConsumerService(room_name=room_name)
        if not self.room_service.room_exist():
            self.close(status.HTTP_404_NOT_FOUND)
        self.accept()

    def receive_json(self, content):
        message = content
        print(content)
        serializer = RoomInputSerializer(data=message)
        if not serializer.is_valid():
            print('invalid_data')
            return
        print(serializer.validated_data)
        self.send(text_data=json.dumps({
            'value': message
        }))
