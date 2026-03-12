from django.shortcuts import render
from django.http import HttpResponseRedirect, JsonResponse
from users.models import User
from chats.models import Chat, ChatData
import json
from redis import Redis



