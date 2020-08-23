import json

from asgiref.sync import async_to_sync
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
    evaluation = serializers.IntegerField()


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=128)
    password = serializers.CharField(max_length=128)


class RoomConsumer(JsonWebsocketConsumer):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.username: str = ""
        self.room_service: RoomConsumerService = None

    def connect(self):
        room_name = self.scope['url_route']['kwargs']['room_name']
        if not RoomConsumerService.room_exist(room_name):
            self.close(status.HTTP_404_NOT_FOUND)
        async_to_sync(self.channel_layer.group_add)("chat", self.channel_name)
        self.accept()

    def _login(self, username, password):
        room_name = self.scope['url_route']['kwargs']['room_name']
        is_password_valid = RoomConsumerService.password_valid(room_name, password)
        self.scope['session']['logged'] = RoomConsumerService.password_valid(room_name, password)
        self.send_json({'error': "WrongPassword"}) if not is_password_valid else None
        self.scope['session']['username'] = username
        self.scope['session'].save()

    def receive_json(self, content):
        serializer: InputSerializer = InputSerializer(data=content)
        if not serializer.is_valid():
            self.send_json(None)
            return
        data = serializer.validated_data
        if data['input_type'] == LOGIN:
            login_serializer = LoginSerializer(data=data['content'])
            if login_serializer.is_valid():
                login_data = login_serializer.validated_data
                self._login(login_data['username'], login_data['password'])
            else:
                return
        if not self.scope["session"].get("logged", None):
            self.send_json({'error': "NotLogged"})
            return
        if data['input_type'] == SEND_EVALUATION:
            evaluation_serializer = EvaluationSerializer(data=data['content'])
            if evaluation_serializer.is_valid():
                self.send_evaluation_to_group(user=self.scope['session']['username'],
                                              evaluation=evaluation_serializer.validated_data['evaluation'])

    def send_evaluation_to_group(self, user, evaluation):
        async_to_sync(self.channel_layer.group_send)(
            "chat",
            {
                "type": "evaluation.update",
                "value": {
                    'user': user,
                    'evaluation': evaluation
                }
            },
        )

    def evaluation_update(self, event):
        self.send_json(event['value'])

    def disconnect(self, code):
        async_to_sync(self.channel_layer.group_discard)("chat", self.channel_name)

