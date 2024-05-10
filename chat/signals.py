from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Message


@receiver(post_save, sender=Message)
def add_user_to_channel(sender, instance, created, **kwargs):
    if created:
        if instance.subchannel is not None:
            # Check if the subchannel is associated with a channel directly
            if instance.subchannel.channel is not None:
                channel = instance.subchannel.channel
                if instance.sender not in channel.admins.all() and instance.sender != channel.host:
                    channel.members.add(instance.sender)
                    channel.save()
                else:
                    print("Sender is an admin or the host of the channel.")
            # Check if the subchannel is associated with a channel through a category
            elif instance.subchannel.category is not None and instance.subchannel.category.channel_root is not None:
                channel = instance.subchannel.category.channel_root
                if instance.sender not in channel.admins.all() and instance.sender != channel.host:
                    channel.members.add(instance.sender)
                    channel.save()
                else:
                    print("Sender is an admin or the host of the channel.")
            else:
                print("Warning: Subchannel is not associated with a channel directly or through a category.")
        else:
            print("Warning: Message was saved without a subchannel.")
