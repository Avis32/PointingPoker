from django.urls import re_path

from pointing_poker.views import consumers

websocket_urlpatterns = [
    re_path(r'ws/room/(?P<room_name>\w+)/$', consumers.RoomConsumer),
]
