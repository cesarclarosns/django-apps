from . import views

from django.urls import path


app_name = "encyclopedia"
urlpatterns = [
    path("create", views.create, name="create"),
    path("random", views.random_entry, name="random"),
    path("wiki/<str:q>", views.render_entry, name="render_entry"),
    path("wiki/<str:q>/edit", views.edit, name="edit"),
    path("", views.index, name="index")
]
