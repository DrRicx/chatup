from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group

from .models import *

admin.site.unregister(Group)
admin.site.site_header = "ChatUP"

