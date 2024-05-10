from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
import random
import string

from django.urls import reverse


# Create your models here.
def get_profile_image_filepath(self, filename):
    """
    Returns the profile picture with the primary key
    :param self:
    :param filename:
    :return:
    """
    return f'profile_images/{self.pk}/{"profile_image.png"}'


def get_default_profile_image():
    """
    Set a default profile image for each user
    :return:
    """
    return "profilePictureDefault/default_profile.png"


class Account(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_picture = models.ImageField(null=True, blank=True, upload_to=get_profile_image_filepath,
                                        default=get_default_profile_image)
    gender = models.CharField(
        max_length=6,
        choices=[('MALE', 'male'), ('FEMALE', 'female')]
    )
    student_number = models.CharField(max_length=12, null=True, blank=True)
    middle_name = models.CharField(max_length=12, null=True, blank=True)

    def __str__(self):
        return self.user.username

    def get_profile_filename(self):
        """
        Change the upload picture name into 'profile_image'
        :return:
        """
        return str(self.profile_picture)[str(self.profile_picture).index(f'profile_images/{self.pk}/'):]


class Channels(models.Model):
    host = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    channel_name = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)
    is_private = models.BooleanField(default=False)
    members = models.ManyToManyField(User, related_name='channel_members', blank=True)
    admins = models.ManyToManyField(User, related_name='channel_admins')

    # messages = models.ForeignKey(Message, on_delete=models.CASCADE) # Uncomment this if you have a Message model

    def __str__(self):
        return self.channel_name

    def add_admin(self, user):
        self.admins.add(user)

    def remove_admin(self, user):
        self.admins.remove(user)


class PinnedChannel(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
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
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    recipient = models.ForeignKey(User, related_name='received_messages', null=True, blank=True,
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
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.ForeignKey(Message, on_delete=models.CASCADE)
    subchannel = models.ForeignKey(SubChannel, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('user', 'message', 'subchannel')

    def __str__(self):
        return f"{self.user.username} favourited {self.message.content[:50]} in {self.subchannel.subchannel_name}"

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


class FriendList(models.Model):
    userFriend = models.OneToOneField(User, on_delete=models.CASCADE, related_name="user")
    friends = models.ManyToManyField(User, blank=True, related_name="friends")

    def __str__(self):
        return self.userFriend.username

    def add_friend(self, account):
        """
        Add a friend(other user) tot the User Friend list
        Only add if the user is not already in the friend list
        :param account:
        :return:
        """
        if not account in self.friends.all():
            self.friends.add(account)
            self.save()

    def remove_friend(self, account):
        """
        Removes the friend(user)
        :param account:
        :return:
        """
        self.friends.remove(account)
        self.save()

    def unfriend(self, removee):
        remover_friends_list = self
        remover_friends_list.remove_friend(removee)
        friends_list = FriendList.objects.get(user=removee)
        friends_list.remove_friend(self.userFriend)

    def is_mutual_friend(self, friend):
        """
        Return True is both User are friends
        :param friend:
        :return:
        """
        if friend in self.friends.all():
            return True
        return False


class FriendRequest(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sender")
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name="receiver")
    is_active = models.BooleanField(blank=True, null=False, default=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.sender.username

    def accept(self):
        receiver_friend_list = FriendList.objects.get(user=self.receiver)
        if receiver_friend_list:
            receiver_friend_list.add_friend(self.sender)
            sender_friend_list = FriendList.objects.get(user=self.sender)
            if sender_friend_list:
                sender_friend_list.add_friend(self.receiver)
                self.is_active = False
                self.save()

    def decline(self):
        """
        Decline a friend request
        It is decline by settings the 'is_active' field to False
        :return:
        """
        self.is_active = False
        self.save()

    def cancel(self):
        """
        Cancel a friend request
        It is 'cancelled' by setting the 'is_active' field to False
        Only different with respect to 'declining' through the notification that is generated
        :return:
        """
        self.is_active = False
        self.save()
