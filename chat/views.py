from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.core import serializers
from django.http import HttpResponse, HttpResponseRedirect
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from .forms import *
from .friend_request_status import *
from .models import *


def splashPage(request):
    """
    This function is used to render the splash page
    :param request:
    :return:
    """
    # Get the channel instance
    channel = Channels.objects.first()

    # Get the admins of the channel
    admins = channel.admins.all()

    context = {'channel': channel, 'admins': admins}
    return render(request, "chat/splash-page.html", context)


def loginPage(request):
    """
    Handles the login page
    :param request:
    :return:
    """

    pin = PinnedChannel.objects.all()

    if request.method == "POST":
        user = authenticate(username=request.POST.get('username'), password=request.POST.get('password'))
        if user is None:
            messages.error(request, "Invalid Password")
        else:
            login(request, user)
            messages.success(request, "User authenticated and logged in")
        return redirect('channels')
    return render(request, 'chat/register_login.html', {'page': 'login', 'pin': pin})


def registerPage(request):
    """
    Handles the registration page. Responsible for creating new account.
    :param request:
    :return:
    """

    if request.method == 'POST':
        form = UserAccountForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            # Redirect to a success page or login page
            return redirect('login')
    else:
        form = UserAccountForm()

    context = {'form': form}
    return render(request, 'chat/register_login.html', context)


def logoutPage(request):
    """
    Logout the user then redirect them into the home page
    :param request:
    :return:
    """
    logout(request)
    redirect('splashPage')


def accountPage(request, *args, **kwargs):
    context = {}
    user_id = kwargs.get("user_id")

    try:
        account = Account.objects.get(pk=user_id)
    except Account.DoesNotExist:
        return HttpResponse("User cannot be found/doesn't exist")

    context['id'] = account.id
    context['username'] = account.user.username

    # Fetch profile picture and student number
    try:
        profile = Account.objects.get(user=account.user)
        context['profile_picture'] = profile.profile_picture.url
        context['student_number'] = profile.student_number
    except Account.DoesNotExist:
        context['profile_picture'] = None
        context['student_number'] = None

    # Fetch the channels where the user is a host
    host_channels = Channels.objects.filter(host=account.user)
    context['host_channels'] = host_channels

    member_channels = Channels.objects.filter(members=account.user)
    context['member_channels'] = member_channels

    return render(request, 'chat/account.html', context)


def createChannelPage(request):
    if request.method == "POST":
        form = ChannelForm(request.POST, user=request.user)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = ChannelForm(user=request.user)
    context = {'form': form}
    return render(request, 'chat/channel/create_channel.html', context)


def homePage(request):
    channels = Channels.objects.all()
    context = {'channels': channels}
    return render(request, 'chat/home.html', context)


def channelPage(request):
    channels = Channels.objects.all()
    user = User.objects.all
    context = {'user': user}

    # Create a dictionary to store each channel and its associated subchannels
    channel_subchannels = {}

    for channel in channels:
        # Filter the subchannels based on the current channel and where category is None
        subchannels = SubChannel.objects.filter(channel=channel, category=None)
        # Add the channel and its subchannels to the dictionary
        channel_subchannels[channel] = subchannels

    # Add the dictionary to the context
    context['channel_subchannels'] = channel_subchannels

    return render(request, 'chat/channel/channel.html', context)


def deleteChannel(request, pk):
    channel = Channels.objects.get(id=pk)
    if request.user in channel.admins.all() or channel.host == request.user:
        channel.delete()
        return redirect('channels')
    else:
        return HttpResponse("You do not have the permission to delete")


def categoryPage(request, channel_id):
    channel = Channels.objects.get(id=channel_id)
    categories = Categories.objects.filter(channel_root=channel)

    # Create a dictionary to store each category and its associated subchannels
    category_subchannels = {}

    for category in categories:
        # Filter the subchannels based on the current category
        subchannels = SubChannel.objects.filter(category=category)
        # Add the category and its subchannels to the dictionary
        category_subchannels[category] = subchannels

    context = {'category_subchannels': category_subchannels, 'channel': channel}
    return render(request, 'chat/category/category.html', context)


def createCategory(request, channel_id):
    channel = Channels.objects.get(id=channel_id)
    if request.method == "POST":
        form = CategoryForm(request.POST, channel=channel)
        if form.is_valid():
            category_name = form.cleaned_data.get('category')
            if Categories.category_exists(channel, category_name):
                messages.error(request, "Category already exists.")
            else:
                form.save()
                return redirect('categoryPage', channel_id=channel_id)
    else:
        form = CategoryForm(channel=channel)
    context = {'form': form, 'channel': channel}
    return render(request, 'chat/category/category_creation.html', context)


def deleteCategory(request, category_id):
    category = Categories.objects.get(id=category_id)
    channel = category.channel_root
    if request.user in channel.admins.all() or channel.host == request.user:
        category.delete()
        return redirect('categoryPage', channel_id=channel.id)
    else:
        return HttpResponse("You do not have the permission to delete")


def createSubChannel(request, channel_id, category_id=None):
    channel = Channels.objects.get(id=channel_id)
    category = None
    if category_id is not None:
        category = Categories.objects.get(id=category_id)
    if request.method == "POST":
        form = SubChannelForm(request.POST, channel=channel, category=category)
        if form.is_valid():
            subchannel_name = form.cleaned_data.get('subchannel_name')
            # Check if a subchannel with the same name already exists in the given channel or category
            if SubChannel.objects.filter(subchannel_name=subchannel_name, category=category, channel=channel).exists():
                messages.error(request, "SubChannel already exists in this channel or category.")
            else:
                subchannel = form.save(commit=False)  # Don't immediately save the form
                subchannel.channel = channel  # Manually set the channel
                subchannel.save()  # Now save the form
                if category:
                    return redirect('categoryPage', channel_id=channel_id)
                else:
                    return redirect('channels')
    else:
        form = SubChannelForm(channel=channel, category=category)
    context = {'form': form, 'channel': channel}
    return render(request, 'chat/subchannel/subchannel_creation.html', context)


def subChannelPage(request, channel_id):
    channel = Channels.objects.get(id=channel_id)
    subchannels = SubChannel.objects.filter(channel=channel)
    return render(request, 'chat/category', {'subchannels': subchannels})


def deleteSubChannel(request, subchannel_id):
    try:
        subchannel = SubChannel.objects.get(id=subchannel_id)
    except SubChannel.DoesNotExist:
        return HttpResponse("Subchannel does not exist")

    if subchannel.category is not None:
        category = subchannel.category
        if request.user in category.channel_root.admins.all() or category.channel_root.host == request.user:
            subchannel.delete()
            return redirect('categoryPage', channel_id=category.channel_root.id)
        else:
            return HttpResponse("You do not have the permission to delete")
    elif subchannel.channel is not None:
        channel = subchannel.channel
        if request.user in channel.admins.all() or channel.host == request.user:
            subchannel.delete()
            return redirect('channelPage', channel_id=channel.id)
        else:
            return HttpResponse("You do not have the permission to delete")
    else:
        return HttpResponse("Subchannel is not associated with a category or a channel")


def get_messages(request, subchannel_name):
    messages = Message.objects.filter(subchannel__subchannel_name=subchannel_name).order_by('timestamp')
    messages_list = list(messages.values('content', 'sender__username', 'timestamp'))
    return JsonResponse(messages_list, safe=False)


def direct_message_view(request, user_id, subchannel_id=None):
    recipient = get_object_or_404(User, id=user_id)
    subchannel = None
    if subchannel_id is not None:
        subchannel = get_object_or_404(SubChannel, id=subchannel_id)

    if request.method == "POST":
        content = request.POST.get('content')
        Message.objects.create(content=content, sender=request.user, recipient=recipient, subchannel=subchannel)
        return redirect('direct_message', user_id=user_id)

    if subchannel:
        messages = Message.objects.filter(subchannel=subchannel).order_by('timestamp')
    else:
        messages = Message.objects.filter(sender=recipient, recipient=request.user) | Message.objects.filter(
            sender=request.user, recipient=recipient)
        messages = messages.order_by('timestamp')

    return render(request, 'chat/direct_message.html', {'messages': messages, 'recipient_username': recipient.username})


def subchannelRoom(request, unique_key):
    if request.headers.get('x-requested-with') != 'XMLHttpRequest' and request.method == 'GET':
        return HttpResponseRedirect(reverse('home'))

    subchannel = SubChannel.objects.filter(unique_key=unique_key).first()
    if subchannel is None:
        return HttpResponse("Subchannel not found")
    messages = Message.objects.filter(subchannel=subchannel).order_by('timestamp')
    context = {'subchannel': subchannel, 'messages': messages}
    return render(request, 'chat/subchannel/subchannel.html', context)


def subchannels_json(request, channel_id):
    if request.method == 'GET':
        subchannels = SubChannel.objects.filter(channel_id=channel_id)
        subchannel_list = [{'id': sub.id, 'name': sub.subchannel_name, 'unique_key': sub.unique_key} for sub in
                           subchannels]
        response_data = {
            'channel_id': channel_id,
            'subchannels': subchannel_list
        }
        return JsonResponse(response_data, safe=False)
    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)


def subchannelPage(request, subchannel_key):
    subchannels = get_object_or_404(id=subchannel_key)
    context = {'subchannels': subchannels}
    return render(request, 'chat/subchannelPage.html', context)


def pin_channel(request, channel_id):
    channel = Channels.objects.get(id=channel_id)
    pinned = PinnedChannel.pin_channel(request.user, channel)
    if pinned:
        messages.success(request, f'Successfully pinned {channel.channel_name}.')
    else:
        messages.error(request, f'{channel.channel_name} is already pinned.')
    return redirect(request.META.get('HTTP_REFERER', 'home'))

def unpin_channel(request, channel_id):
    channel=Channels.objects.filter(id=channel_id)
    unpinned=PinnedChannel.unpin_channel(request.user, channel)
    if unpinned:
        messages.success(request, f'Successfully unpinned {channel.channel_name}')
    else:
        messages.error(request, f'{channel.channel_name} is not pinned')
    return redirect(request.META.get('HTTP_REFERER', 'home'))