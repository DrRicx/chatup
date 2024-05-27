from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group

from .models import *

# Add any other configurations you want here
# Register your models here.

admin.site.unregister(Group)
admin.site.site_header = "ChatUP"


class CustomUserInline(admin.StackedInline):
    model = Account
    can_delete = False
    verbose_name_plural = 'Account'


class CustomUserAdmin(UserAdmin):
    inlines = (CustomUserInline,)


# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)


@admin.register(Channels)
class ChannelsAdmin(admin.ModelAdmin):
    list_display = ('channel_name', 'host', 'is_private')
    search_fields = ('channel_name', 'host')
    list_filter = ('created', 'host')


admin.site.register(Categories)
@admin.register(SubChannel)
class SubChannelAdmin(admin.ModelAdmin):
    list_display = ('subchannel_name', 'channel')
    search_fields = ('subchannel_name', 'channel')
    list_filter = ('created', 'channel')

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('content', 'sender', 'recipient', 'subchannel')
    search_fields = ('content', 'subchannel')
    list_filter = ('content', 'subchannel')


@admin.register(FavouriteMessage)
class FavouriteMessageAdmin(admin.ModelAdmin):
    list_display = ('message', 'user', 'subchannel')
    search_fields = ('subchannel', 'user')
    list_filter = ('subchannel', 'user')


@admin.register(PinnedChannel)
class PinnedChannelAdmin(admin.ModelAdmin):
    list_display = ('channel', 'user')
    search_field = ('channel', 'user')
    list_filter = ('channel', 'user')
