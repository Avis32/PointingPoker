import json
from channels.generic.websocket import JsonWebsocketConsumer
from rest_framework import serializers, status

from pointing_poker.services.room_service import RoomConsumerService

LOGIN = 'login'
SEND_EVALUATION = 'send_evaluation'


Inputs = (
    LOGIN,
    SEND_EVALUATION,
)


class InputSerializer(serializers.Serializer):
    input_type = serializers.ChoiceField(choices=Inputs)
    content = serializers.DictField(required=True)


class EvaluationSerializer(serializers.Serializer):
    evaluation = serializers.IntegerField


class LoginSerializer(serializers.Serializer):
    password = serializers.CharField


class RoomConsumer(JsonWebsocketConsumer):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.username: str = ""
        self.room_service: RoomConsumerService = None

    def connect(self):
        self.scope["session"]['logged'] = False
        self.scope["session"].save()
        room_name = self.scope['url_route']['kwargs']['room_name']
        if not RoomConsumerService.room_exist(room_name):
            self.close(status.HTTP_404_NOT_FOUND)
        self.accept()

    def login(self, password):
        room_name = self.scope['url_route']['kwargs']['room_name']
        self.scope["session"]['logged'] = RoomConsumerService.login(room_name, password)

    def receive_json(self, content):
        serializer: InputSerializer = InputSerializer(data=content)
        if not serializer.is_valid():
            self.send_json(serializer.errors)
            print("errors" * 20)
            print(serializer.errors)
            return
        data = serializer.validated_data
        print('T'*20)
        print(data)
        if data.input_type == LOGIN:
            print("login")
            pass
        if not self.scope["session"].get("logged"):
            print("not logged")
            self.send(text_data=json.dumps(None))
            return

        self.send(text_data=json.dumps({
            'value': content
        }))
