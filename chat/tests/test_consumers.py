# from channels.testing import WebsocketCommunicator
# from channels.db import database_sync_to_async
# from django.test import AsyncTestCase
# from django.contrib.auth.models import User
# from chat.models import Room, Message
# from wassup.asgi import application

# class TestChatConsumer(AsyncTestCase):

#     async def asyncSetUp(self):
#         # run before each test
#         self.user = await database_sync_to_async(User.objects.create_user)(
#             username='testuser', password='secret'
#         )
#         self.room = await database_sync_to_async(Room.objects.create)(
#             name='Room1', owner=self.user
#         )

#     async def test_connect_and_send_message(self):
#         communicator = WebsocketCommunicator(
#             application=application,
#             path=f"/ws/chat/{self.room.id}/"
#         )
#         communicator.scope['user'] = self.user
#         connected, _ = await communicator.connect()
#         self.assertTrue(connected, "User should be able to connect")

#         await communicator.send_json_to({'message': 'Hello world'})
#         response = await communicator.receive_json_from()
#         self.assertEqual(response['message'], 'Hello world')

#         # Check database
#         msg_count = await database_sync_to_async(Message.objects.count)()
#         self.assertEqual(msg_count, 1)

#         await communicator.disconnect()

# #TODO
