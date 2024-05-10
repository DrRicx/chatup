from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import *


# Add any other configurations you want here
# Register your models here.
class CustomUserInline(admin.StackedInline):
    model = Account
    can_delete = False
    verbose_name_plural = 'Account'


class CustomUserAdmin(UserAdmin):
    inlines = (CustomUserInline,)


# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)


class FriendListAdmin(admin.ModelAdmin):
    list_filter = ['userFriend']
    list_display = ['userFriend']
    search_fields = ['userFriend']
    readonly_fields = ['userFriend']

    class Meta:
        model = FriendList


admin.site.register(FriendList, FriendListAdmin)


class FriendRequestAdmin(admin.ModelAdmin):
    list_filter = ['sender', 'receiver']
    list_display = ['sender', 'receiver']
    search_fields = ['sender__username', 'receiver__username']

    class Meta:
        model = FriendRequest


admin.site.register(FriendRequest, FriendRequestAdmin)
admin.site.register(Channels)
admin.site.register(Categories)
admin.site.register(SubChannel)
admin.site.register(Message)
admin.site.register(FavouriteMessage)
admin.site.register(PinnedChannel)