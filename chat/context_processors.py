from django.contrib.admin import site

from django.db.models import Count
from django.db.models.functions import TruncDay
from .models import *

def chat_context_processor(request):
    messages_per_day = Message.objects.annotate(day=TruncDay('timestamp')).values('day').annotate(c=Count('id')).order_by('day')
    users_per_day = User.objects.annotate(day=TruncDay('date_joined')).values('day').annotate(c=Count('id')).order_by('day')
    channels_per_day = Channels.objects.annotate(day=TruncDay('created')).values('day').annotate(c=Count('id')).order_by('day')

    # Create lists for dates and counts
    dates = [str(item['day']) for item in messages_per_day]
    message_counts = [item['c'] for item in messages_per_day]
    user_counts = [item['c'] for item in users_per_day]
    channel_counts = [item['c'] for item in channels_per_day]

    return {
        'message_count': Message.objects.count(),
        'user_count': User.objects.count(),
        'channel_count': Channels.objects.count(),
        'dates': dates,
        'message_counts': message_counts,
        'user_counts': user_counts,
        'channel_counts': channel_counts,
    }

def admin_context(request):
    return {'app_list': site.get_app_list(request)}