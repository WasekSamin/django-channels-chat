from gettext import find
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q

from core.quick_sort import quick_sort
from .models import *
from account.models import *
from core.find_object import find_obj
from copy import deepcopy
from .random_slug_generator import random_slug_generator


# Find all the chat nofication where request.user is as receiver
def find_user_chat_notification_list(copied_chat_notify_list, item_list, receiver):
    notified_obj = find_obj(copied_chat_notify_list, "receiver_email", receiver.email, 0, len(copied_chat_notify_list))

    if notified_obj is not None:
        if notified_obj["message_seen"] == False:
            item_list.append(notified_obj["sender_email"])
        copied_chat_notify_list.remove(notified_obj)
        return find_user_chat_notification_list(copied_chat_notify_list, item_list, receiver)
    return item_list


# Adding all the accounts with notification info
def find_user_with_notified_list(accounts, notified_list, notified_account_list):
    for account in accounts:
        if account["email"] in notified_list:
            notified_account_list.append({
                "account": account,
                "notify": True
            })
        else:
            notified_account_list.append({
                "account": account,
                "notify": False
            })

    return notified_account_list


# Fetching last message between each account and the current user
def find_accounts_with_last_msg(accounts, last_msg_list, current_user):
    for account in accounts:
        account_obj = Account(**account["account"])
        last_msg = Chat.objects.filter(Q(sender=current_user, receiver=account_obj) | Q(sender=account_obj, receiver=current_user)).last()
        message = None
        if last_msg:
            message = last_msg.message
        else:
            message = "There is no message yet!"
        last_msg_list.append({
            "account": account["account"],
            "notify": account["notify"],
            "last_msg": message
        })
    return last_msg_list


### For group ####
# Find all the groups that request.user is joined in
def find_user_connected_groups(group_chatroom_list, group_list, current_user):
    group_list = [group for group in group_chatroom_list if current_user in group["users"].all()]
    return group_list


# Find all the group message seen list for current user
def find_user_group_msg_seen_list(group_msg_seen_list, user_group_list, group_list):
    for group in user_group_list:
        group_msg_seen_obj = find_obj(group_msg_seen_list, "room", group["room"], 0, len(group_msg_seen_list))

        if group_msg_seen_obj is not None:
            group_msg_seen_obj = GroupChatMessageSeen(**group_msg_seen_obj)
            group_list.append({
                "group": group,
                "group_message_seen": group_msg_seen_obj
            })
        else:
            group_list.append({
                "group": group,
                "group_message_seen": None
            })
    return group_list


# Find all the group message seen with notification for current user
def find_user_group_with_notified_list(group_msg_seen_list, group_list, current_user):
    for msg_seen in group_msg_seen_list:
        if msg_seen["group_message_seen"] is not None and current_user in msg_seen["group_message_seen"].users.all():
            group_list.append({
                "group": msg_seen["group"],
                "notify": False
            })
        elif msg_seen["group_message_seen"] is not None:
            group_list.append({
                "group": msg_seen["group"],
                "notify": True
            })
        else:
            group_list.append({
                "group": msg_seen["group"],
                "notify": False
            })
    return group_list


# Find all the last message of the group of current user
def find_user_group_last_msg(user_group_list, last_msg_list):
    for group in user_group_list:
        last_msg = GroupChat.objects.filter(room=group["group"]["room"]).last()

        message = None
        if last_msg:
            message = last_msg.message
        else:
            message = "There is no message yet!"
        
        last_msg_list.append({
            "group": group["group"],
            "notify": group["notify"],
            "last_msg": message
        })
    return last_msg_list


# Update group message notification for current user
def update_group_message_seen(group_msg_seen_list, room, current_user):
    group_msg_seen_obj = find_obj(group_msg_seen_list, "room", room, 0, len(group_msg_seen_list))

    if group_msg_seen_obj is not None:
        group_msg_seen_obj = GroupChatMessageSeen(**group_msg_seen_obj)

        if current_user not in group_msg_seen_obj.users.all():
            group_msg_seen_obj.users.add(current_user.id)

            return True
    return False


class HomeView(LoginRequiredMixin, View):
    login_url = '/account/login/'

    def get(self, request):
        accounts = Account.objects.values()
        chat_nofifies = ChatMessageSeen.objects.all()
        chat_notify_list = list(map(lambda i: {
            "id": i.id,
            "room": i.room,
            "chatroom": i.chatroom,
            "sender": i.sender,
            "receiver": i.receiver,
            "message_seen": i.message_seen,
            "sender_email": i.sender_email,
            "receiver_email": i.receiver_email
        }, chat_nofifies))

        copied_chat_notify_list = deepcopy(chat_notify_list)
        item_list = []
        # Find all the chat nofication where request.user is as receiver
        get_user_with_notify_list = find_user_chat_notification_list(copied_chat_notify_list, item_list, request.user)
        # print(get_user_with_notify_list)
        notified_account_list = []
        # Adding all the accounts with notification info
        get_user_notified_list = find_user_with_notified_list(accounts, get_user_with_notify_list, notified_account_list)
        # print(get_user_notified_list)
        last_msg_list = []
        # Fetching last message between each account and the current user
        get_accounts_with_notify_and_last_msg = find_accounts_with_last_msg(get_user_notified_list, last_msg_list, request.user)
        # print(get_accounts_with_notify_and_last_msg)

        ##### For group #####
        group_chatrooms = GroupChatroom.objects.all()
        group_chatroom_list = list(map(lambda i: {
            "id": i.id,
            "room": i.room,
            "given_room_name": i.given_room_name,
            "creator": i.creator,
            "users": i.users,
            "created_at": i.created_at
        }, group_chatrooms))

        # Show all the groups that request.user is joined in
        group_list = []
        get_user_connected_group_list = find_user_connected_groups(group_chatroom_list, group_list, request.user)

        # User group notified list
        group_msg_seens = GroupChatMessageSeen.objects.values()
        group_msg_seen_list = list(map(lambda i: i, group_msg_seens))

        group_list = []
        # Find all the group message seen list for current user
        find_group_msg_seen_list = find_user_group_msg_seen_list(group_msg_seen_list, get_user_connected_group_list, group_list)
        # print(find_group_msg_seen_list)
        group_list = []
        # Find all the group message seen with notification for current user
        find_user_group_with_notify_list = find_user_group_with_notified_list(find_group_msg_seen_list, group_list, request.user)
        # print(find_user_group_with_notify_list)
        last_msg_list = []
        # Find all the last message of the group of current user
        find_user_group_last_msg_with_notify = find_user_group_last_msg(find_user_group_with_notify_list, last_msg_list)
        # print(find_user_group_last_msg_with_notify)

        args = {
            "accounts": get_accounts_with_notify_and_last_msg,
            "groups": find_user_group_last_msg_with_notify,
        }
        return render(request, "chat/home.html", args)


def find_room_all_chats(copied_chat_list, item_list, room):
    chat_obj = find_obj(copied_chat_list, "room", room, 0, len(copied_chat_list))

    if chat_obj is not None:
        item_list.append(chat_obj)
        copied_chat_list.remove(chat_obj)
        return find_room_all_chats(copied_chat_list, item_list, room)
    return item_list


# Update chat notification status
def update_message_notification(room, sender):
    chat_notifications = ChatMessageSeen.objects.all()
    chat_notification_list = list(map(lambda i: {
        "id": i.id,
        "room": i.room,
        "chatroom": i.chatroom,
        "sender": i.sender,
        "receiver": i.receiver,
        "message_seen": i.message_seen,
        "sender_email": i.sender_email,
        "receiver_email": i.receiver_email,
        "created_at": i.created_at
    }, chat_notifications))

    chat_notifiy_obj = find_obj(chat_notification_list, "room", room, 0, len(chat_notification_list))

    if chat_notifiy_obj is not None:
        chat_notifiy_obj = ChatMessageSeen(**chat_notifiy_obj)

        if chat_notifiy_obj.sender.email != sender.email and chat_notifiy_obj.receiver.email == sender.email:
            chat_notifiy_obj.message_seen = True
            chat_notifiy_obj.save()

            return True
    return False


class ChatroomView(LoginRequiredMixin, View):
    login_url = "/account/login/"

    def get(self, request, room):
        accounts = Account.objects.values()
        chat_nofifies = ChatMessageSeen.objects.all()
        chat_notify_list = list(map(lambda i: {
            "id": i.id,
            "room": i.room,
            "chatroom": i.chatroom,
            "sender": i.sender,
            "receiver": i.receiver,
            "message_seen": i.message_seen,
            "sender_email": i.sender_email,
            "receiver_email": i.receiver_email
        }, chat_nofifies))

        copied_chat_notify_list = deepcopy(chat_notify_list)
        item_list = []
        # Find all the chat nofication where request.user is as receiver
        get_user_with_notify_list = find_user_chat_notification_list(copied_chat_notify_list, item_list, request.user)
        # print(get_user_with_notify_list)
        notified_account_list = []
        # Adding all the accounts with notification info
        get_user_notified_list = find_user_with_notified_list(accounts, get_user_with_notify_list, notified_account_list)
        last_msg_list = []
        # Fetching last message between each account and the current user
        get_accounts_with_notify_and_last_msg = find_accounts_with_last_msg(get_user_notified_list, last_msg_list, request.user)
        # print(get_accounts_with_notify_and_last_msg)

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

        # Update notification status
        chat_notify_status = update_message_notification(chatroom_obj["room"], request.user)
        # print(chat_notify_status)

        # user1 -> Myself
        # user2 -> The other person with I am chatting
        user1, user2 = None, None

        if chatroom_obj is not None:
            if request.user.email == chatroom_obj["user1"].email:
                user1 = chatroom_obj["user1"]
                user2 = chatroom_obj["user2"]
            else:
                user1 = chatroom_obj["user2"]
                user2 = chatroom_obj["user1"]

            if user1.email != request.user.email and user2.email != request.user.email:
                return redirect("chat:home")

            chats = Chat.objects.all()
            chat_list = list(map(lambda i: {
                "id": i.id,
                "room": i.room,
                "chatroom": i.chatroom,
                "sender": i.sender,
                "receiver": i.receiver,
                "message": i.message,
                "created_at": i.created_at.strftime("%b %d, %Y %I:%M %p")
            }, chats))

            copied_chats = deepcopy(chat_list)
            item_list = []
            get_chat_list = find_room_all_chats(copied_chats, item_list, chatroom_obj["room"])
            # print(get_chat_list)
            quick_sort(get_chat_list, "id", 0, len(get_chat_list) - 1)

            ##### For group #####
            group_chatrooms = GroupChatroom.objects.all()
            group_chatroom_list = list(map(lambda i: {
                "id": i.id,
                "room": i.room,
                "given_room_name": i.given_room_name,
                "creator": i.creator,
                "users": i.users,
                "created_at": i.created_at
            }, group_chatrooms))

            # Show all the groups that request.user is joined in
            group_list = []
            get_user_connected_group_list = find_user_connected_groups(group_chatroom_list, group_list, request.user)

            # User group notified list
            group_msg_seens = GroupChatMessageSeen.objects.values()
            group_msg_seen_list = list(map(lambda i: i, group_msg_seens))

            group_list = []
            # Find all the group message seen list for current user
            find_group_msg_seen_list = find_user_group_msg_seen_list(group_msg_seen_list, get_user_connected_group_list, group_list)
            # print(find_group_msg_seen_list)
            group_list = []
            # Find all the group message seen with notification for current user
            find_user_group_with_notify_list = find_user_group_with_notified_list(find_group_msg_seen_list, group_list, request.user)
            # print(find_user_group_with_notify_list)
            last_msg_list = []
            # Find all the last message of the group of current user
            find_user_group_last_msg_with_notify = find_user_group_last_msg(find_user_group_with_notify_list, last_msg_list)
            # print(find_user_group_last_msg_with_notify)

        args = {
            "accounts": get_accounts_with_notify_and_last_msg,
            "groups": find_user_group_last_msg_with_notify,
            "user1": user1,
            "user2": user2,
            "chats": get_chat_list,
            "chat_notify_status": chat_notify_status
        }
        return render(request, "chat/chat.html", args)


class CreateChatroomView(LoginRequiredMixin, View):
    login_url = "/account/login/"

    def get(self, request, user_id):
        accounts = Account.objects.values()
        account_list = list(map(lambda i: i, accounts))

        user1 = request.user
        user2 = find_obj(account_list, "id", user_id, 0, len(account_list))

        if user2 is not None:
            concat_user = f"{user1.email.split('@')[0]}{user2['email'].split('@')[0]}"
            # print(concat_user)

            chatrooms = Chatroom.objects.values()
            chatroom_list = list(map(lambda i: i, chatrooms))

            # For user1 + user2
            chatroom_obj = find_obj(
                chatroom_list, "concat_user", concat_user, 0, len(chatroom_list))

            # If chatroom already exists
            if chatroom_obj is not None:
                return redirect(f"/chat/{chatroom_obj['room']}")
            else:
                # For user2 + user1
                concat_user = f"{user2['email'].split('@')[0]}{user1.email.split('@')[0]}"

                chatroom_obj = find_obj(
                    chatroom_list, "concat_user", concat_user, 0, len(chatroom_list))

                if chatroom_obj is not None:
                    return redirect(f"/chat/{chatroom_obj['room']}")
                # Create a new chatroom
                else:
                    room = random_slug_generator(chatroom_list, "room")
                    concat_user = f"{user1.email.split('@')[0]}{user2['email'].split('@')[0]}"

                    user2 = Account(**user2)

                    chatroom_obj = Chatroom(
                        room=room,
                        concat_user=concat_user,
                        user1=user1,
                        user2=user2
                    )
                    chatroom_obj.save()

                    return redirect(f"/chat/{chatroom_obj.room}/")
        else:
            return redirect("chat:home")


class CreateMessageView(LoginRequiredMixin, View):
    login_url = "/account/login/"

    def post(self, request):
        json_resp = {"error": False}

        return JsonResponse(json_resp, safe=False)


class GroupChatroomView(LoginRequiredMixin, View):
    login_url = "/account/login/"

    def get(self, request, room):
        #### For accounts #####
        accounts = Account.objects.values()
        chat_nofifies = ChatMessageSeen.objects.all()
        chat_notify_list = list(map(lambda i: {
            "id": i.id,
            "room": i.room,
            "chatroom": i.chatroom,
            "sender": i.sender,
            "receiver": i.receiver,
            "message_seen": i.message_seen,
            "sender_email": i.sender_email,
            "receiver_email": i.receiver_email
        }, chat_nofifies))

        copied_chat_notify_list = deepcopy(chat_notify_list)
        item_list = []
        # Find all the chat nofication where request.user is as receiver
        get_user_with_notify_list = find_user_chat_notification_list(copied_chat_notify_list, item_list, request.user)
        # print(get_user_with_notify_list)
        notified_account_list = []
        # Adding all the accounts with notification info
        get_user_notified_list = find_user_with_notified_list(accounts, get_user_with_notify_list, notified_account_list)
        # print(get_user_notified_list)
        last_msg_list = []
        # Fetching last message between each account and the current user
        get_accounts_with_notify_and_last_msg = find_accounts_with_last_msg(get_user_notified_list, last_msg_list, request.user)
        # print(get_accounts_with_notify_and_last_msg)

        #### For groups ####
        group_chatrooms = GroupChatroom.objects.all()
        group_chatroom_list = list(map(lambda i: {
            "id": i.id,
            "room": i.room,
            "given_room_name": i.given_room_name,
            "creator": i.creator,
            "users": i.users,
            "created_at": i.created_at
        }, group_chatrooms))
        
        group_chatroom_obj = find_obj(group_chatroom_list, "room", room, 0, len(group_chatroom_list))

        if group_chatroom_obj:
            group_users = group_chatroom_obj["users"].all()

            group_chats = GroupChat.objects.all()
            group_chat_list = list(map(lambda i: {
                "id": i.id,
                "room": i.room,
                "group_chatroom": i.group_chatroom,
                "sender": i.sender,
                "message": i.message,
                "created_at": i.created_at.strftime("%b %d, %Y %I:%M %p")
            }, group_chats))

            # If user is in the group
            if request.user in group_users:
                copied_group_chats = deepcopy(group_chat_list)
                item_list = []
                get_chat_list = find_room_all_chats(copied_group_chats, item_list, group_chatroom_obj["room"])
                quick_sort(get_chat_list, "id", 0, len(get_chat_list) - 1)

                ##### For group #####
                # Show all the groups that request.user is joined in
                group_list = []
                get_user_connected_group_list = find_user_connected_groups(group_chatroom_list, group_list, request.user)

                # User group notified list
                group_msg_seens = GroupChatMessageSeen.objects.values()
                group_msg_seen_list = list(map(lambda i: i, group_msg_seens))

                group_list = []
                # Find all the group message seen list for current user
                find_group_msg_seen_list = find_user_group_msg_seen_list(group_msg_seen_list, get_user_connected_group_list, group_list)
                # print(find_group_msg_seen_list)
                group_list = []
                # Find all the group message seen with notification for current user
                find_user_group_with_notify_list = find_user_group_with_notified_list(find_group_msg_seen_list, group_list, request.user)
                # print(find_user_group_with_notify_list)
                last_msg_list = []
                # Find all the last message of the group of current user
                find_user_group_last_msg_with_notify = find_user_group_last_msg(find_user_group_with_notify_list, last_msg_list)
                # print(find_user_group_last_msg_with_notify)

                # Update group message seen notification
                update_group_message_notification = update_group_message_seen(group_msg_seen_list, group_chatroom_obj["room"], request.user)

                # chat_notify_list
            else:   # --> Else if user not in the group, redirect to home page
                return redirect("chat:home")
        else:
            return redirect("chat:home")

        args = {
            "accounts": get_accounts_with_notify_and_last_msg,
            "groups": find_user_group_last_msg_with_notify,
            "group_chatroom_obj": group_chatroom_obj,
            "chats": get_chat_list,
            "group_notify_status": update_group_message_notification,
        }
        return render(request, "chat/group_chat.html", args)
