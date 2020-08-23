import pytest
from asgiref.sync import async_to_sync, sync_to_async
from channels.testing import WebsocketCommunicator
from rest_framework.exceptions import ErrorDetail

from PointingPoker.asgi import application
from pointing_poker.models import Room
from pointing_poker.views.consumers import SEND_EVALUATION, LOGIN



@pytest.mark.django_db
class TestConsumers:
    def setup_method(self):
        self.not_connected_communicator: WebsocketCommunicator = WebsocketCommunicator(application, "/ws/room/test/")

    @pytest.fixture
    async def setup_one_not_connected_consumer(self):
        room = Room(room_name='test', password='pass')
        await sync_to_async(room.save)()
        communicator = WebsocketCommunicator(application, "/ws/room/test/")
        yield communicator
        await sync_to_async(room.delete)()
        await communicator.disconnect()

    @pytest.fixture
    async def setup_one_consumer(self):
        room = Room(room_name='test', password='pass')
        await sync_to_async(room.save)()
        communicator = WebsocketCommunicator(application, "/ws/room/test/")
        await communicator.connect()
        yield communicator
        await sync_to_async(room.delete)()
        await communicator.disconnect()

    @pytest.fixture
    async def setup_two_consumers(self):
        room = Room(room_name='test', password='pass')
        await sync_to_async(room.save)()
        communicator1 = WebsocketCommunicator(application, "/ws/room/test/")
        communicator2 = WebsocketCommunicator(application, "/ws/room/test/")
        await communicator1.connect()
        await communicator2.connect()
        communicators = [communicator1, communicator2]
        for idx, communicator in enumerate(communicators):
            await communicator.send_json_to({
                'input_type': LOGIN,
                'content': {
                    'password': 'pass',
                    'username': 'user' + str(idx)
                }
            })
        yield communicators
        await sync_to_async(room.delete)()
        await communicator1.disconnect()
        await communicator2.disconnect()

    @pytest.mark.asyncio
    async def test_if_socket_connect(self, setup_one_not_connected_consumer):
        connected, _ = await setup_one_not_connected_consumer.connect()
        assert connected

    @pytest.mark.asyncio
    async def test_if_socket_disconnect_when_room_does_not_exists(self):
        communicator = WebsocketCommunicator(application, "/ws/room/nonexisting/")
        connected, _ = await communicator.connect()
        assert not connected
        await communicator.disconnect()

    @pytest.mark.asyncio
    async def test_if_socket_gives_error_when_wrong_password_on_login(self, setup_one_consumer):
        communicator = setup_one_consumer
        await communicator.connect()
        await communicator.send_json_to({
            'input_type': LOGIN,
            'content': {
                'password': 'wrong',
                'username': 'Marek'
            }
        })
        data = await communicator.receive_json_from()
        assert data == {'error': 'WrongPassword'}

    @pytest.mark.asyncio
    async def test_if_socket_gives_error_when_wrong_password_on_login(self, setup_one_consumer):
        communicator = setup_one_consumer
        await communicator.connect()
        await communicator.send_json_to({
            'input_type': LOGIN,
            'content': {
                'password': 'wrong',
                'username': 'Marek'
            }
        })
        data = await communicator.receive_json_from()
        assert data == {'error': 'WrongPassword'}


    @pytest.mark.asyncio
    async def test_if_socket_send_eval_to_other_consumer(self, setup_two_consumers):
        communicator1, communicator2 = setup_two_consumers
        await communicator1.send_json_to({
            'input_type': SEND_EVALUATION,
            'content': {
                'evaluation': 2,
            }
        })
        data = await communicator2.receive_json_from()
        print(data)
        assert data == {'user': 'user0', 'evaluation': 2}









