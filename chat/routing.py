from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/channels/(?P<unique_key>[^/]+)/$', consumers.ChatConsumer.as_asgi()),
    re_path(r'ws/direct_message/(?P<user_id>[^/]+)/$', consumers.ChatConsumer.as_asgi()),
]