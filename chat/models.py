from django.db import models
from datetime import datetime
from django.contrib.auth import get_user_model
from django.dispatch import receiver

User = get_user_model()


class Chatroom(models.Model):
    room = models.SlugField(max_length=20, null=True, unique=True)
    concat_user = models.CharField(max_length=200, null=True)
    user1 = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user1")
    user2 = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user2")
    created_at = models.DateTimeField(default=datetime.now)

    def __str__(self):
        return self.room


class Chat(models.Model):
    room = models.SlugField(max_length=20, null=True)
    chatroom = models.ForeignKey(Chatroom, on_delete=models.CASCADE, related_name="chatroom")
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sender")
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name="receiver")
    message = models.TextField(null=True)
    created_at = models.DateTimeField(default=datetime.now)

    def __str__(self):
        return str(self.id)


class ChatMessageSeen(models.Model):
    room = models.SlugField(max_length=20, null=True)
    chatroom = models.OneToOneField(Chatroom, on_delete=models.CASCADE, related_name="chatroom_chat_message_seen")
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sender_chat_message_seen")
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name="receiver_chat_message_seen")
    message_seen = models.BooleanField(default=False)
    sender_email = models.EmailField(null=True, blank=True)
    receiver_email = models.EmailField(null=True, blank=True)
    created_at = models.DateTimeField(default=datetime.now)

    def __str__(self):
        return self.room


class GroupChatroom(models.Model):
    room = models.SlugField(max_length=20, null=True, unique=True)
    given_room_name = models.CharField(max_length=200, null=True)
    creator = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="creator")
    users = models.ManyToManyField(User)
    created_at = models.DateTimeField(default=datetime.now)

    def __str__(self):
        return self.room


class GroupChat(models.Model):
    room = models.SlugField(max_length=20, null=True)
    group_chatroom = models.ForeignKey(GroupChatroom, on_delete=models.CASCADE, related_name="group_chatroom")
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="group_sender")
    receiver = models.ManyToManyField(User, blank=True)
    message = models.TextField(null=True)
    created_at = models.DateTimeField(default=datetime.now)

    def __str__(self):
        return str(self.id)


class GroupChatMessageSeen(models.Model):
    room = models.SlugField(max_length=20, null=True)
    group_chatroom = models.OneToOneField(GroupChatroom, on_delete=models.CASCADE, related_name="group_chatroom_chat_message_seen")
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="group_sender_message_seen")
    receiver = models.ManyToManyField(User, blank=True)
    created_at = models.DateTimeField(default=datetime.now)

    def __str__(self):
        return self.room