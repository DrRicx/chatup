# chat/urls.py
from django.urls import path
from django.contrib.auth import views as auth_views

from . import views

urlpatterns = [
    path("", views.splashPage, name="splashPage"),

    path("register/", views.registerPage, name="register"),
    path("login/", views.loginPage, name="login"),
    path("logout/", views.logoutPage, name="logout"),

    path("home/", views.homePage, name="home"),

    path("account/<str:user_id>/", views.accountPage, name="account"),

    path("create_channel/", views.createChannelPage, name="addChannel"),
    path("delete_channel/<str:pk>", views.deleteChannel, name="deleteChannel"),
    path('channels/<int:channel_id>/create_category/', views.createCategory, name='create_category'),
    path("channels/", views.channelPage, name="channels"),
    path("channels/<int:channel_id>/categories/", views.categoryPage, name="categoryPage"),

    path('deleteCategory/<int:category_id>/', views.deleteCategory, name='deleteCategory'),
    path('deleteSubChannel/<int:subchannel_id>/', views.deleteSubChannel, name='deleteSubChannel'),

    # chat/urls.py
    path("channels/<int:channel_id>/categories/<int:category_id>/create_subchannel/", views.createSubChannel,
         name="createSubChannel"),
    path("channels/<int:channel_id>/create_subchannel/", views.createSubChannel, name="createSubChannelChannel"),

    path("channels/<int:channel_id>", views.subchannels_json, name="subchannels_json"),
    path("channels/<str:unique_key>", views.subchannelRoom, name="subchannelRoom"),

    path("channels/<int:channel_id>/subchannels/", views.subChannelPage, name="subChannelPage"),

    path('pin_channel/<int:channel_id>/', views.pin_channel, name='pin_channel'),
    path('unpin_channel/<int:channel_id>/', views.unpin_channel, name='unpin_channel'),

    path('favourite_message_in_subchannel/<int:message_id>/<int:subchannel_id>/', views.favouriteMessageSubchannel, name='favourite_message_in_subchannel'),
    path('unfavourite_message_in_subchannel/<int:message_id>/<int:subchannel_id>/', views.unFavouriteMessageSubchannel, name='unfavourite_message_in_subchannel'),

    path('get_messages/<str:subchannel_name>/', views.get_messages, name='get_messages'),
    path('direct_message/<int:user_id>/', views.direct_message_view, name='direct_message'),
    # Password reset path/urls
    path('password_change/done/',
         auth_views.PasswordChangeDoneView.as_view(template_name='chat/password_reset/password_change_done.html'),
         name='password_change_done'),

    path('password_change/',
         auth_views.PasswordChangeView.as_view(template_name='chat/password_reset/password_change.html'),
         name='password_change'),

    path('password_reset/done/',
         auth_views.PasswordResetCompleteView.as_view(template_name='chat/password_reset/password_reset_done.html'),
         name='password_reset_done'),

    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),

    path('reset/done/',
         auth_views.PasswordResetCompleteView.as_view(template_name='chat/password_reset/password_reset_complete.html'),
         name='password_reset_complete'),
]
