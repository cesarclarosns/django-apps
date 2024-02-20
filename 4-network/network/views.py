import json
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt

from .models import User, Post


def index(request):
    
    # Authenticated users can view posts
    if request.user.is_authenticated:
        return render(request, "network/index.html")
    
    # Everyone else is prompted to sign in
    else:
        return HttpResponseRedirect(reverse("login"))


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")
    

@csrf_exempt
@login_required
def compose(request):
    if request.method != "POST":
        return JsonResponse({"error": "Only POST request allowed."}, status=400)
    
    # Load form data
    data = json.loads(request.body)
    # The post content cannot be empty
    if data.get("content") == "":
        return JsonResponse({"error": "Form content is empty."}, status=400)
    
    # Crete new post
    post = Post(user=request.user, content=data.get("content"))
    post.save()
    
    print(post)

    return JsonResponse({"message": "Post created succesfully."}, status=201)


@csrf_exempt
@login_required
def edit(request, post_id):
    if request.method != "PUT":
        return JsonResponse({"error": "Only POST request allowed."}, status=400)
    
    # Load form data
    data = json.loads(request.body)
    if data is None:
        return JsonResponse({"error": "Form content is empty."})
    # Try to get the post object
    try:
        post = Post.objects.get(pk=post_id)
    except:
        return JsonResponse({"error": "Post not found."}, status=400)
    
    # The post can only be edited by the user who posted it
    if post.user.id != request.user.id:
        return JsonResponse({"error": "Invalid request."}, status=400)
    
    post.content = data.get("content")
    post.save()
    
    return JsonResponse({"message": "Post edited succesfully!."}, status=201)
        

@csrf_exempt
def post(request, post_id):
    if request.method != "GET":
        return JsonResponse({"error": "Only GET request allowed."}, status=400)
    
    try:
        post = Post.objects.get(pk=post_id)
    except:
        return JsonResponse({"error": "Post not found."}, status=400)
    
    return JsonResponse(post.serialize(), status=201)


@csrf_exempt
def posts(request, type):
    if request.method != "GET":
        return JsonResponse({"error": "GET request required."}, 
                            status=400)
    
    if type == "all":
        # Get all posts
        posts = Post.objects.all().order_by("-timestamp")
        return JsonResponse([post.serialize() for post in posts], 
                            safe=False)
    elif type == "following":
        # Get all posts from users being followed
        posts = request.user.posts_users_followed()
        return JsonResponse([post.serialize() for post in posts],
                            safe=False)
    else:
        return JsonResponse({"error": "Invalid request."}, 
                            status=400)


@csrf_exempt
def posts_profile(request, user_id):
    if request.method != "GET":
        return JsonResponse({"error": "GET request required."}, 
                            status=400)
    # Try to get the user with id user_id
    try:
        user = User.objects.get(pk=user_id)
    except:
        return JsonResponse({"error": "Invalid user_id."}, 
                            status=400)
    
    return JsonResponse(user.serialize(), safe=False)
    
    
@csrf_exempt
@login_required
def react(request, post_id, action):
    if request.method != "PUT":
        return JsonResponse({"error": "PUT request required."}, status=400)
    if action not in ["like", "unlike"]:
        return JsonResponse({"error": "Invalid action."}, status=401)
    
    # Try to get the post with id post_id
    try:
        post = Post.objects.get(pk=post_id)
    except:
        return JsonResponse({"error": "Invalid post id."}, status=400)
    
    # Manage "like" action
    if action == "like":
        if request.user in post.reacted.all():
            return JsonResponse({"error": "User has already reacted to this post."})
        post.reacted.add(request.user)
        return JsonResponse({"message": "Liked."}, status=201)
    # Manage "unlike" action
    else:
        if request.user not in post.reacted.all():
            return JsonResponse({"error": "User has not reacted to this post."})
        post.reacted.remove(request.user)
        return JsonResponse({"message": "Unliked."}, status=201)
    

@csrf_exempt
@login_required
def follow(request, user_id, action):
    if request.method != "PUT":
        return JsonResponse({"error": "PUT request required."}, status=400)
    
    # Users cannot follow themselves
    if request.user.id == user_id:
        return JsonResponse({"error": "Invalid action."}, status=400)
    # Try to get the user with id user_id
    try:
        user = User.objects.get(pk=user_id)
    except:
        return JsonResponse({"error": "Invalid user id."}, status=400)   

    if action == "follow" and request.user not in user.followers.all():
        user.followers.add(request.user)
        return JsonResponse({"message": "Succes."}, status=201)
    elif action == "unfollow" and request.user in user.followers.all():
        user.followers.remove(request.user)
        return JsonResponse({"message": "Succes."}, status=201)
    else:
        return JsonResponse({"error": "Invalid action."}, status=400)
    
