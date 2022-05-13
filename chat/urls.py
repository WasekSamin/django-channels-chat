from django.urls import path

from .views import *

app_name = "chat"
urlpatterns = [
    path("", HomeView.as_view(), name="home"),
    path("chat/<str:room>/", ChatroomView.as_view(), name="chatroom"),
    path("create-chatroom/<int:user_id>/", CreateChatroomView.as_view(), name="create-chatroom"),
    path("create-message/", CreateMessageView.as_view(), name="create-message"),
]