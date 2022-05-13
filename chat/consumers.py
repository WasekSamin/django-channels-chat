from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.db import database_sync_to_async
from account.models import Account
from .models import *
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
        print(f"{data=}")
        privateChat = data.get("privateChat", None)

        # Joining a group
        if data["command"] == "join":
            # Joining publicly
            await self.channel_layer.group_add(
                "public",
                self.channel_name
            )
            self.groups.append("public")
            
            # For private chat
            if privateChat:
                room_name = data["groupName"].split("/")[-2]

                await self.channel_layer.group_add(
                    room_name,
                    self.channel_name
                )
                self.groups.append(room_name)

                print("GROUPS:", self.groups)

            for group in self.groups:
                # Trigger when user connect to socket
                await self.channel_layer.group_send(
                    group,
                    {
                        "type": "user.connect",  # This is a function name. '.' represents '_'
                        "connect": True,
                        "user_id": self.scope["user"].id
                    }
                )
        # Send message
        elif data["command"] == "send":
            room = data["room"].split("/")[-2]
            # print(room)

            chat_obj = await database_sync_to_async(self.create_message)(sender=self.scope["user"], room=room, message=data["message"])
            
            if chat_obj is not None:
                await self.channel_layer.group_send(
                    "public",
                    {
                        "type": "send.message",
                        "room": chat_obj.room,
                        "message": chat_obj.message,
                        "sender_username": chat_obj.sender.username,
                        "sender_id": chat_obj.sender.id,
                        "receiver_id": chat_obj.receiver.id,
                        "created_at": chat_obj.created_at.strftime("%b %d, %Y %I:%M %p"),
                        "create_message_success": True
                    }
                )
        elif data["command"] == "receive_message":
            if self.scope["user"].id == data["receiver_id"]:
                receiver_current_loc = data["receiverCurrentLoc"]

                send_data = {
                    "type": "receive.message",
                    "room": data["room"],
                    "message": data["message"],
                    "sender_username": data["sender_username"],
                    "sender_id": data["sender_id"],
                    "receiver_id": data["receiver_id"],
                    "created_at": data["created_at"],
                    "receive_message_success": True
                }
                
                # If receiver on home page
                if receiver_current_loc == "home":
                    send_data["show_as_notification"] = True
                    send_data["append_to_message_field"] = False

                    await self.channel_layer.group_send(
                        "public",
                        send_data
                    )

                    await database_sync_to_async(self.chatMessageNotify)(sender_id=send_data["sender_id"], room=send_data["room"], receiver=self.scope["user"])
                # If receiver on a chatroom
                elif receiver_current_loc == "chatroom":
                    send_data["show_as_notification"] = False
                    send_data["append_to_message_field"] = True
                    current_loc = data["currentLoc"].split("/")[-2]

                    # If receiver in the correct/same chat room
                    if current_loc == data["room"]:
                        await self.channel_layer.group_send(
                            data["room"],
                            send_data
                        )
                    # If receiver in other chatroom
                    else:
                        await self.channel_layer.group_send(
                            "public",
                            send_data
                        )
                        
                        await database_sync_to_async(self.chatMessageNotify)(sender_id=send_data["sender_id"], room=send_data["room"], receiver=self.scope["user"])


    async def disconnect(self, data):
        print(f"{self.scope['user']} is disconnected!")
        print(self.groups)
        # print("DISCONNECT FROM GROUP:", self.group_name)
        await database_sync_to_async(self.update_user_status)(email=self.scope["user"].email, is_online=False)
        # # Trigger when user get disconnect from socket
        for group in self.groups:
            await self.channel_layer.group_send(
                group,
                {
                    "type": "user.disconnect",
                    "disconnect": True,
                    "user_id": self.scope["user"].id
                }
            )


    async def user_connect(self, event):
        # print(f"{event=}")
        await self.send_json({
            "connect": event["connect"],
            "user_id": event["user_id"]
        })
        await database_sync_to_async(self.update_user_status)(email=self.scope["user"].email, is_online=True)


    async def user_disconnect(self, event):
        # print(event)
        await self.send_json({
            "disconnect": event["disconnect"],
            "user_id": event["user_id"]
        })


    # Create message
    def create_message(self, sender, room, message):
        chatrooms = Chatroom.objects.all()
        chatroom_list = list(map(lambda i: {
            "id": i.id,
            "room": i.room,
            "concat_user": i.concat_user,
            "user1": i.user1,
            "user2": i.user2,
            "created_at": i.created_at
        }, chatrooms))

        chatroom_obj = find_obj(chatroom_list, "room", room, 0, len(chatroom_list))

        if chatroom_obj is not None:
            chatroom_obj = Chatroom(**chatroom_obj)

            receiver = None
            if sender.email == chatroom_obj.user1.email:
                receiver = chatroom_obj.user2
            else:
                receiver = chatroom_obj.user1

            chat_obj = Chat(
                room=room,
                chatroom=chatroom_obj,
                sender=sender,
                receiver=receiver,
                message=message
            )
            chat_obj.save()

            return chat_obj
        return None


    # For sending message
    async def send_message(self, event):
        # print(event)

        await self.send_json({
            "room": event["room"],
            "message": event["message"],
            "sender_username": event["sender_username"],
            "sender_id": event["sender_id"],
            "receiver_id": event["receiver_id"],
            "created_at": event["created_at"],
            "create_message_success": event["create_message_success"]
        })


    # For receiving message
    async def receive_message(self, event):
        # print(self.scope["user"])
        # print(f"{event=}")
        
        if self.scope["user"].id == event["receiver_id"]:
            await self.send_json({
                "room": event["room"],
                "message": event["message"],
                "sender_username": event["sender_username"],
                "sender_id": event["sender_id"],
                "receiver_id": event["receiver_id"],
                "created_at": event["created_at"],
                "receive_message_success": event["receive_message_success"],
                "show_as_notification": event["show_as_notification"],
                "append_to_message_field": event["append_to_message_field"]
            })


    # For message notify
    def chatMessageNotify(self, sender_id, room, receiver):
        print("FROM NOTIFICATION!")
        
        accounts = Account.objects.values()
        account_list = list(map(lambda i: i, accounts))
        
        chat_notifications = ChatMessageSeen.objects.values()
        chat_notification_list = list(map(lambda i: i, chat_notifications))

        sender = find_obj(account_list, "id", sender_id, 0, len(account_list))
        print(sender)

        chat_notify_obj = find_obj(chat_notification_list, "room", room, 0, len(chat_notification_list))
        print(chat_notify_obj)

        if sender is not None:
            sender = Account(**sender)
            # If chat notification object already exists
            if chat_notify_obj is not None:
                chat_notify_obj = ChatMessageSeen(**chat_notify_obj)

                chat_notify_obj.sender = sender
                chat_notify_obj.receiver = receiver
                chat_notify_obj.message_seen = False
                chat_notify_obj.sender_email = sender.email
                chat_notify_obj.receiver_email = receiver.email
                chat_notify_obj.save()
            else:   # -> Else create a new chat notification object
                chatrooms = Chatroom.objects.values()
                chatroom_list = list(map(lambda i: i, chatrooms))

                chatroom_obj = find_obj(chatroom_list, "room", room, 0, len(chatroom_list))
                print(chatroom_obj)
                chatroom_obj = Chatroom(**chatroom_obj)

                ChatMessageSeen.objects.create(
                    room=room,
                    chatroom=chatroom_obj,
                    sender=sender,
                    receiver=receiver,
                    sender_email=sender.email,
                    receiver_email=receiver.email
                )
