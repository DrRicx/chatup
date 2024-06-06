from datetime import timezone
from django.contrib.auth.models import User, Permission
from django.db import models
from django.conf import settings
from django.apps import apps
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.contenttypes.models import ContentType
import random
import string
from django.urls import reverse
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin


def get_default_profile_path(instance, filename):
    """
    Returns the path where the channel picture will be stored.
    :param instance: The Channels model instance.
    :param filename: The original name of the uploaded file.
    :return: Path to store the file.
    """
    return "channelPictureDefault/channel_default.png"


class Channels(models.Model):
    host = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    channel_name = models.CharField(max_length=200)
    channel_picture = models.ImageField(upload_to=get_default_profile_path, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)
    is_private = models.BooleanField(default=False)
    members = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='channel_members', blank=True)
    admins = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='channel_admins')

    # messages = models.ForeignKey(Message, on_delete=models.CASCADE) # Uncomment this if you have a Message model

    def __str__(self):
        return self.channel_name

    def save(self, *args, **kwargs):
        if not self.channel_picture:
            self.channel_picture = get_default_profile_path(self, 'default_profile.png')
        super().save(*args, **kwargs)

    def add_admin(self, user):
        self.admins.add(user)

    def remove_admin(self, user):
        self.admins.remove(user)


class PinnedChannel(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    channel = models.ForeignKey(Channels, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('user', 'channel')

    def __str__(self):
        return f"{self.user.username} pinned {self.channel.channel_name}"

    @classmethod
    def pin_channel(cls, user, channel):
        if not cls.objects.filter(user=user, channel=channel).exists():
            cls.objects.create(user=user, channel=channel)
            return True
        return False

    @classmethod
    def unpin_channel(cls, user, channel):
        try:
            pin = cls.objects.get(user=user, channel=channel)
            pin.delete()
            return True
        except cls.DoesNotExist:
            return False

    @classmethod
    def is_channel_pinned(cls, user, channel):
        return cls.objects.filter(user=user, channel=channel).exists()


class Categories(models.Model):
    channel_root = models.ForeignKey(Channels, on_delete=models.SET_NULL, null=True)
    category = models.CharField(max_length=200)

    @classmethod
    def category_exists(cls, channel, category_name):
        return cls.objects.filter(channel_root=channel, category=category_name).exists()

    def __str__(self):
        if self.channel_root is not None:
            return f"{self.channel_root.channel_name} - {self.category}"
        else:
            return f"No Channel - {self.category}"


class SubChannel(models.Model):
    category = models.ForeignKey(Categories, on_delete=models.SET_NULL, null=True, blank=True)
    channel = models.ForeignKey(Channels, on_delete=models.SET_NULL, null=True, blank=True)
    subchannel_name = models.CharField(max_length=200)
    created = models.DateTimeField(auto_now_add=True)
    unique_key = models.CharField(max_length=50, unique=True, blank=True)

    def __str__(self):
        return f"{self.subchannel_name}"

    @staticmethod
    def generate_unique_key():
        while True:
            unique_key = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(50))
            if not SubChannel.objects.filter(unique_key=unique_key).exists():
                return unique_key

    def save(self, *args, **kwargs):
        if not self.unique_key:
            self.unique_key = self.generate_unique_key()
        super().save(*args, **kwargs)


class Message(models.Model):
    content = models.TextField()
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='received_messages', null=True, blank=True,
                                  on_delete=models.SET_NULL)
    timestamp = models.DateTimeField(auto_now_add=True)
    subchannel = models.ForeignKey(SubChannel, null=True, blank=True, on_delete=models.CASCADE)

    def __str__(self):
        if self.subchannel:
            return f"From {self.sender.username} in {self.subchannel.subchannel_name}: {self.content[:50]}"
        else:
            return f"From {self.sender.username} to {self.recipient.username if self.recipient else 'subchannel'}: {self.content[:50]}"

    def get_absolute_url(self):
        return reverse('message_detail_view', args=[str(self.id)])


class FavouriteMessage(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    message = models.ForeignKey(Message, on_delete=models.CASCADE)
    subchannel = models.ForeignKey(SubChannel, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('user', 'message', 'subchannel')

    def __str__(self):
        return f"{self.user.username} favourited {self.message.content[:50]} in {self.subchannel.subchannel_name}"

    @classmethod
    def is_favourited(cls, user, message, subchannel):
        """
        Method to check if a message is favourited by a user in a specific subchannel.
        :param user: The user to check for.
        :param message: The message to check.
        :param subchannel: The subchannel to check in.
        :return: True if the message is favourited, False otherwise.
        """
        return cls.objects.filter(user=user, message=message, subchannel=subchannel).exists()

    @classmethod
    def favourite_message(cls, user, message, subchannel):
        """
        Method to add favourite message. If the messages is already in the list in relation to the user and subchannel, it simply return False. Otherwise, add the message in the list
        :param user:
        :param message:
        :param subchannel:
        :return:
        """
        if not cls.objects.filter(user=user, message=message, subchannel=subchannel).exists():
            cls.objects.create(user=user, message=message, subchannel=subchannel)
            return True
        return False

    @classmethod
    def unfavourite_message(cls, user, message, subchannel):
        """
        Method to remove a favourite message. If the message is not in the list, it simply return False. Otherwise, remove the message from the list
        :param user:
        :param message:
        :param subchannel:
        :return:
        """
        try:
            favourite = cls.objects.get(user=user, message=message, subchannel=subchannel)
            favourite.delete()
            return True
        except cls.DoesNotExist:
            return False
