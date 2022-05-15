import account
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.db import database_sync_to_async
from account.models import Account
from .models import *
from core.find_object import find_obj
from django.shortcuts import redirect
from .random_slug_generator import random_slug_generator


class ChatConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        await self.accept()
        # print(f"{self.scope['user']} joined!")

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
        # print(f"{data=}")
        private_chat = data.get("privateChat", None)
        group_create = data.get("groupCreate", None)
        group_chat = data.get("groupChat", None)

        # Joining a group
        if data["command"] == "join":
            # Joining publicly
            await self.channel_layer.group_add(
                "public",
                self.channel_name
            )
            self.groups.append("public")
            
            # For private chat
            if private_chat:
                room_name = data["groupName"].split("/")[-2]

                await self.channel_layer.group_add(
                    room_name,
                    self.channel_name
                )
                self.groups.append(room_name)

                # print("GROUPS:", self.groups)
            elif group_create:
                room_name = data["roomName"]
                users = data["users"]

                await self.channel_layer.group_send(
                    "public",
                    {
                        "type": "group.create",
                        "room_name": room_name,
                        "users": users,
                        "creatorId": data["creatorId"]
                    }
                )
            elif group_chat:
                room_name = data["groupName"].split("/")[-2]

                await self.channel_layer.group_add(
                    room_name,
                    self.channel_name
                )
                self.groups.append(room_name)

                # print("GROUPS:", self.groups)

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
        # Send message -> Private chat
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
        # Send message -> Group chat
        elif data["command"] == "group_send":
            room = data["room"].split("/")[-2]

            group_chat_obj, group_chatroom_id, receive_users = await database_sync_to_async(self.group_create_message)(sender=self.scope["user"], room=room, message=data["message"])

            if group_chat_obj is not None and group_chatroom_id is not None and receive_users is not None:
                await self.channel_layer.group_send(
                    "public",
                    {
                        "type": "send.group.message",
                        "group_id": group_chatroom_id,
                        "room": group_chat_obj.room,
                        "message": group_chat_obj.message,
                        "sender_username": group_chat_obj.sender.username,
                        "sender_id": group_chat_obj.sender.id,
                        "created_at": group_chat_obj.created_at.strftime("%b %d, %Y %I:%M %p"),
                        "receive_users": receive_users,
                        "group_create_message_success": True
                    }
                )
        # Receive message -> Private chat
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
        # Receive message -> Group chat
        elif data["command"] == "group_receive_message":
            if self.scope["user"].id in data["receive_users"]:
                # print(self.scope["user"].id, "is in the group message")
                receiver_current_loc = data["receiverCurrentLoc"]

                send_data = {
                    "type": "group.receive.message",
                    "group_id": data["group_id"],
                    "room": data["room"],
                    "message": data["message"],
                    "sender_username": data["sender_username"],
                    "sender_id": data["sender_id"],
                    "receive_users": data["receive_users"],
                    "receiver_id": self.scope["user"].id,
                    "created_at": data["created_at"],
                    "group_receive_message_success": True
                }
                
                # If receiver on home page
                if receiver_current_loc == "home" or receiver_current_loc == "privateChatroom":
                    send_data["show_as_notification"] = True
                    send_data["append_to_message_field"] = False

                    await self.channel_layer.group_send(
                        "public",
                        send_data
                    )

                    await database_sync_to_async(self.group_chat_message_notify)(sender_id=send_data["sender_id"], room=send_data["room"], receiver=self.scope["user"], seen=False)
                # If receiver on a group chatroom
                elif receiver_current_loc == "group_chatroom":
                    send_data["show_as_notification"] = False
                    send_data["append_to_message_field"] = True
                    current_loc = data["currentLoc"].split("/")[-2]

                    # If receiver in the correct/same chat room
                    if current_loc == data["room"]:
                        await self.channel_layer.group_send(
                            data["room"],
                            send_data
                        )

                        await database_sync_to_async(self.group_chat_message_notify)(sender_id=send_data["sender_id"], room=send_data["room"], receiver=self.scope["user"], seen=True)
                    # If receiver in other chatroom
                    else:
                        await self.channel_layer.group_send(
                            "public",
                            send_data
                        )
                        
                        await database_sync_to_async(self.group_chat_message_notify)(sender_id=send_data["sender_id"], room=send_data["room"], receiver=self.scope["user"], seen=False)


    async def disconnect(self, data):
        # print(f"{self.scope['user']} is disconnected!")
        # print(self.groups)
        # print("DISCONNECT FROM GROUP:", self.group_name)
        await database_sync_to_async(self.update_user_status)(email=self.scope["user"].email, is_online=False)
        # # Trigger when user get disconnect from socket
        for group in self.groups:
            # print(group)
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


    # Create message for private chat
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


    # Create message for group
    def group_create_message(self, sender, room, message):
        group_chatrooms = GroupChatroom.objects.values()
        group_chatroom_list = list(map(lambda i: i, group_chatrooms))

        group_chatroom_obj = find_obj(group_chatroom_list, "room", room, 0, len(group_chatroom_list))

        if group_chatroom_obj is not None:
            group_chatroom_obj = GroupChatroom(**group_chatroom_obj)

            receive_users = [user.id for user in group_chatroom_obj.users.all()]

            group_chat_obj = GroupChat(
                room=room,
                group_chatroom=group_chatroom_obj,
                sender=sender,
                message=message,
            )
            group_chat_obj.save()

            return group_chat_obj, group_chatroom_obj.id, receive_users
        return None, None, None

    # For sending message -> Private chat
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

    
    # For sending message -> Group chat
    async def send_group_message(self, event):
        await self.send_json({
            "room": event["room"],
            "group_id": event["group_id"],
            "message": event["message"],
            "sender_username": event["sender_username"],
            "sender_id": event["sender_id"],
            "receive_users": event["receive_users"],
            "created_at": event["created_at"],
            "group_create_message_success": event["group_create_message_success"]
        })

    # For receiving message -> Private chat
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


    # For receiving message -> Group chat
    async def group_receive_message(self, event):
        # print("RECEIVER:", self.scope["user"])
        # print(f"{event=}")
        
        if self.scope["user"].id != event["sender_id"]:
            # print(self.scope["user"])
            await self.send_json({
                "group_id": event["group_id"],
                "room": event["room"],
                "message": event["message"],
                "sender_username": event["sender_username"],
                "sender_id": event["sender_id"],
                "receiver_id": event["receiver_id"],
                "created_at": event["created_at"],
                "group_receive_message_success": event["group_receive_message_success"],
                "show_as_notification": event["show_as_notification"],
                "append_to_message_field": event["append_to_message_field"]
            })


    # For message notify -> Private chat
    def chatMessageNotify(self, sender_id, room, receiver):
        # print("FROM NOTIFICATION!")
        
        accounts = Account.objects.values()
        account_list = list(map(lambda i: i, accounts))
        
        chat_notifications = ChatMessageSeen.objects.values()
        chat_notification_list = list(map(lambda i: i, chat_notifications))

        sender = find_obj(account_list, "id", sender_id, 0, len(account_list))
        # print(sender)

        chat_notify_obj = find_obj(chat_notification_list, "room", room, 0, len(chat_notification_list))
        # print(chat_notify_obj)

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
                # print(chatroom_obj)
                chatroom_obj = Chatroom(**chatroom_obj)

                ChatMessageSeen.objects.create(
                    room=room,
                    chatroom=chatroom_obj,
                    sender=sender,
                    receiver=receiver,
                    sender_email=sender.email,
                    receiver_email=receiver.email
                )


    # Message notify -> Group chat
    def group_chat_message_notify(self, sender_id, room, receiver, seen):
        # print("INSIDE GROUP MESSAGE SEEN")
        group_msg_seens = GroupChatMessageSeen.objects.values()
        group_msg_seen_list = list(map(lambda i: i, group_msg_seens))

        group_chatrooms = GroupChatroom.objects.values()
        group_chatroom_list = list(map(lambda i: i, group_chatrooms))

        group_msg_seen_obj = find_obj(group_msg_seen_list, "room", room, 0, len(group_msg_seen_list))

        if group_msg_seen_obj is not None:
            group_msg_seen_obj = GroupChatMessageSeen(**group_msg_seen_obj)

            group_msg_seen_obj.users.add(sender_id)
            
            if seen:
                group_msg_seen_obj.users.add(receiver.id)
            else:
                group_msg_seen_obj.users.remove(receiver.id)
        else:
            group_chatroom_obj = find_obj(group_chatroom_list, "room", room, 0, len(group_chatroom_list))

            if group_chatroom_obj is not None:
                group_chatroom_obj = GroupChatroom(**group_chatroom_obj)

                group_msg_seen_obj = GroupChatMessageSeen(
                    room=room,
                    group_chatroom=group_chatroom_obj,
                )
                group_msg_seen_obj.save()
                group_msg_seen_obj.users.add(sender_id)

                if seen:
                    group_msg_seen_obj.users.add(receiver.id)
                else:
                    group_msg_seen_obj.users.remove(receiver.id)


    # Create group chatroom
    async def group_create(self, event):
        users = event["users"]
        # print("users:", users)
        given_room_name = event["room_name"]
        creatorId = event["creatorId"]

        group_chatroom_obj = await database_sync_to_async(self.create_group)(given_room_name=given_room_name, users=users, creatorId=creatorId)

        if group_chatroom_obj is not None:
            # print(group_chatroom_obj)
            await self.channel_layer.group_send(
                "public",
                {
                    "type": "send.group.chatroom",
                    "group_id": group_chatroom_obj.id,
                    "room": group_chatroom_obj.room,
                    "given_room_name": group_chatroom_obj.given_room_name,
                    "creator": group_chatroom_obj.creator.id,
                    "users": event["users"],
                    "group_created": True
                }
            )


    def create_group(self, given_room_name, users, creatorId):
        # print("FROM CREATE GROUP")

        if self.scope["user"].id == creatorId:
            group_chatrooms = GroupChatroom.objects.values()
            group_chatroom_list = list(map(lambda i: i, group_chatrooms))

            accounts = Account.objects.values()
            account_list = list(map(lambda i: i, accounts))

            account_obj = find_obj(account_list, "id", creatorId, 0, len(account_list))

            if account_obj is not None:
                account_obj = Account(**account_obj)

                room_slug = random_slug_generator(group_chatroom_list, "room")

                group_chatroom_obj = GroupChatroom(
                    room=room_slug,
                    given_room_name=given_room_name,
                    creator=account_obj,
                )
                group_chatroom_obj.save()

                for user in users:
                    group_chatroom_obj.users.add(user)

                return group_chatroom_obj
            return None


    async def send_group_chatroom(self, event):
        await self.send_json({
            "group_id": event["group_id"],
            "room": event["room"],
            "given_room_name": event["given_room_name"],
            "creator": event["creator"],
            "users": event["users"],
            "group_created": event["group_created"]
        })