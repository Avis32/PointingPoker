import pytest
from asgiref.sync import async_to_sync, sync_to_async
from channels.testing import WebsocketCommunicator
from rest_framework.exceptions import ErrorDetail

from PointingPoker.asgi import application
from pointing_poker.models import Room
from pointing_poker.views.consumers import SEND_EVALUATION


@pytest.mark.django_db
class TestConsumers:
    def setup_method(self):
        self.communicator = WebsocketCommunicator(application, "/ws/room/test/")
        async_to_sync(self.communicator.connect)
        print(vars(self.communicator))

    @pytest.fixture
    async def set_up_one_consumer(self):
        self.communicator = WebsocketCommunicator(application, "/ws/room/test/")
        await self.communicator.connect()
        room = Room(room_name='test')
        await sync_to_async(room.save)()
        return 1

    @pytest.fixture
    async def set_up_two_consumer(self):
        self.communicator = WebsocketCommunicator(application, "/ws/room/test/")
        await self.communicator.connect()
        print(vars(self.communicator))
        self.communicator2 = WebsocketCommunicator(application, "/ws/room/test/")
        await self.communicator2.connect()
        print(vars(self.communicator2))
        return 1

    @pytest.mark.asyncio
    async def test_if_socket_connect(self, set_up_one_consumer):
        communicator = WebsocketCommunicator(application, "/ws/room/test/")
        connected, _ = await communicator.connect()
        assert connected

    @pytest.mark.asyncio
    async def test_if_socket_disconnect_when_room_does_not_exists(self, set_up_one_consumer):
        communicator = WebsocketCommunicator(application, "/ws/room/nonexisting/")
        connected, _ = await communicator.connect()
        assert not connected

    @pytest.mark.asyncio
    async def test_if_socket_return_nothing_if_not_logged(self, set_up_one_consumer):
        await self.communicator.send_json_to({
            'input_type': SEND_EVALUATION,
            'content': 'content'
        })
        assert await self.communicator.receive_json_from() is None

    @pytest.mark.asyncio
    async def test_if_sockeat_return_nothing_if_not_logged(self, set_up_one_consumer):
        await self.communicator.send_json_to({
            'input_type': 'wrong',
            'content': {}
        })
        response = await self.communicator.receive_json_from()
        print(response)
        assert type(response['input_type']) == ErrorDetail
        # assert await self.communicator.receive_json_from() is None

    @pytest.mark.asyncio
    async def test_if_logging_work(self, set_up_one_consumer):
        pass





