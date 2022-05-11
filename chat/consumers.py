from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.db import database_sync_to_async
from account.models import Account
from core.find_object import find_obj


class ChatConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        await self.accept()
        print(f"{self.scope['user']} joined!")

    # Updating user online status

    def update_user_status(self, email, is_online):
        accounts = Account.objects.values()
        account_list = list(map(lambda i: i, accounts))

        account_obj = find_obj(account_list, "email",
                               email, 0, len(account_list))

        if account_obj is not None:
            account_obj = Account(**account_obj)
            account_obj.is_online = is_online
            account_obj.save()

    async def receive_json(self, data):
        print(data)

        # Joining a group
        if data["command"] == "join":
            await self.channel_layer.group_add(
                data["groupName"],
                self.channel_name
            )

            # Trigger when user connect to socket
            await self.channel_layer.group_send(
                "public",
                {
                    "type": "user.connect",  # This is a function name. '.' represents '_'
                    "connect": True,
                    "user_id": self.scope["user"].id
                }
            )

    async def disconnect(self, data):
        print(f"{self.scope['user']} is disconnected!")
        await database_sync_to_async(self.update_user_status)(email=self.scope["user"].email, is_online=False)
        # Trigger when user get disconnect from socket
        await self.channel_layer.group_send(
            "public",
            {
                "type": "user.disconnect",
                "disconnect": "true",
                "user_id": self.scope["user"].id
            }
        )

    async def user_connect(self, event):
        print(event)
        await self.send_json({
            "connect": event["connect"],
            "user_id": event["user_id"]
        })
        await database_sync_to_async(self.update_user_status)(email=self.scope["user"].email, is_online=True)

    async def user_disconnect(self, event):
        print(event)
        await self.send_json({
            "disconnect": event["disconnect"],
            "user_id": event["user_id"]
        })
