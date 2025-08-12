from django.shortcuts import render, redirect
from .form import RoomForm
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.contrib.auth.models import User
from .models import Room, Topic, Message

# Create your views here.
def register(request):
    form = UserCreationForm()

    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid:
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            login(request, user)

            return redirect('home')

    context = {'form': form}
    return render(request, 'base/login_form.html', context)

def loginUser(request):
    page = "login"

    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        username = request.POST.get('username').lower()
        password = request.POST.get('password')

        try:
            user = User.objects.get(username=username)
        except:
            messages.error(request, "user not found")
        
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error("username or password does not exist")

    context = {'page': page}
    return render(request, 'base/login_form.html', context)

@login_required(login_url='/login')
def logoutUser(request):
    logout(request)
    return redirect('home')

def home(request):
    q = ''
    
    if request.GET.get('q') != None:
        q = request.GET.get('q')

    rooms = Room.objects.filter(
        Q(topic__name__icontains=q) |
        Q(description__icontains=q) |
        Q(name__icontains=q)
    )

    topics = Topic.objects.all()
    room_count = rooms.count()
    room_messages = Message.objects.filter(
        Q(room__topic__name__icontains=q)
    )

    context = {'rooms': rooms, 'room_count': room_count, 'topics': topics, 'room_messages': room_messages}
    return render(request, 'base/home.html', context)

def room(request, pk):
    room = Room.objects.get(id=pk)

    if request.method == 'POST':
        body = request.POST.get('body')
        Message.objects.create(
            user=request.user,
            room=room,
            body=body
        )

        room.participants.add(request.user)
        return redirect('room', pk=room.id)

    room_messages = room.message_set.all().order_by('-created')
    participants = room.participants.all()

    context = {'room': room, 'room_messages': room_messages, 'participants': participants}
    return render(request, 'base/room.html', context)


def userProfile(request, pk):
    user = User.objects.get(id=pk)
    rooms = user.room_set.all()
    room_messages = user.message_set.all()
    topics = Topic.objects.all()

    context = {'user': user, 'rooms': rooms, 'topics': topics, 'room_messages': room_messages}
    return render(request, 'base/profile.html', context)


@login_required(login_url='/login')
def createRoom(request):
    form = RoomForm()

    if request.method == 'POST':
        form = RoomForm(request.POST)
        if form.is_valid:
            room = form.save(commit=False)
            room.host = request.user
            room.save()
            return redirect('home')

    context = {'form': form}
    return render(request, 'base/room-form.html', context)

@login_required(login_url='/login')
def updateRoom(request, pk):
    room = Room.objects.get(id=pk)
    form = RoomForm(instance=room)

    if request.method == "POST":
        form = RoomForm(request.POST, instance=room)
        if form.is_valid:
            form.save()
            return redirect('home')

    context = {'form': form}
    return render(request, 'base/room-form.html', context)

@login_required(login_url='/login')
def deleteRoom(request, pk):
    room = Room.objects.get(id=pk)
    if request.method == 'POST':
        room.delete()
        return redirect('home')

    return render(request, 'base/delete.html')

def deleteMessage(request, pk):
    message = Message.objects.get(id=pk)
    if request.method == 'POST':
        message.delete()
        return redirect('home')

    return render(request, 'base/delete.html')