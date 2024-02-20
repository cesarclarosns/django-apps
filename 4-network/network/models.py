from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import Q


class User(AbstractUser):
    followers = models.ManyToManyField('self', related_name="following", symmetrical=False)
    
    def serialize(self):
        return {
            "id": self.id,
            "username": self.username,
            "followers": [user.username for user in self.followers.all()],
            "following": [user.username for user in self.following.all()],
            "posts": [post.serialize() for post in self.posts.order_by("-timestamp")],
            "reactions": [post.id for post in self.reactions.all()]
        }
        
    def posts_users_followed(self):
        """
        Returns the posts of users being followed in reverse
        chronological order.
        """
        users_followed_ids = [user.id for user in self.following.all()]
        q_objects = Q()
        for user_id in users_followed_ids:
            q_objects |= Q(user=user_id) # OR the Q objects together
        
        if len(q_objects) > 0:
            posts = Post.objects.filter(q_objects).order_by("-timestamp")
            return posts
        else:
            return []


class Post(models.Model):
    user = models.ForeignKey("User", on_delete=models.CASCADE, related_name="posts")
    content = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    reacted = models.ManyToManyField("User", related_name="reactions")
    
    def serialize(self):
        return {
            "id": self.id,
            "poster_username": self.user.username,
            "poster_id": self.user.id,
            "content": self.content,
            "timestamp": self.timestamp.strftime("%b %d, %I:%M %p"),
            "reacted": [user.username for user in self.reacted.all()]
        }
    
    