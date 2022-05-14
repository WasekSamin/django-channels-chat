from django.contrib import admin

from .models import *

@admin.register(Chatroom)
class ChatroomAdmin(admin.ModelAdmin):
    list_display = (
        "id", "room",
        "concat_user",
        "user1", "user2",
        "created_at"
    )


@admin.register(Chat)
class ChatAdmin(admin.ModelAdmin):
    list_display = (
        "id", "room",
        "chatroom",
        "sender", "receiver",
        "message", "created_at"
    )

@admin.register(ChatMessageSeen)
class ChatMessageSeenAdmin(admin.ModelAdmin):
    list_display = (
        "id", "room",
        "chatroom",
        "sender", "receiver",
        "message_seen",
        "created_at"
    )


@admin.register(GroupChatroom)
class GroupChatroomAdmin(admin.ModelAdmin):
    list_display = (
        "id", "room", "creator",
        "given_room_name", "created_at"
    )


@admin.register(GroupChat)
class GroupChatAdmin(admin.ModelAdmin):
    list_display = (
        "id", "room",
        "group_chatroom",
        "sender",
        "message", "created_at"
    )


@admin.register(GroupChatMessageSeen)
class GroupChatMessageSeenAdmin(admin.ModelAdmin):
    list_display = (
        "id", "room",
        "group_chatroom", 
        "sender", "created_at"
    )