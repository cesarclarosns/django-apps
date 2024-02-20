from django.urls import path
from . import views


urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    
    # API Routes
    path("post/<int:post_id>", views.post, name="post"),
    path("post/create", views.compose, name="compose"),
    path("post/<int:post_id>/<str:action>", views.react, name="react"),
    path("post/edit/<int:post_id>", views.edit, name="edit"),
    path("posts/<int:user_id>", views.posts_profile, name="posts_profile"),
    path("posts/<str:type>", views.posts, name="posts"),   
    path("profile/<int:user_id>/<str:action>", views.follow, name="follow")
]





