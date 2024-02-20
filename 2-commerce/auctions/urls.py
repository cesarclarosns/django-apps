from django.urls import path

from . import views

app_name = 'auctions'
urlpatterns = [
    # Views
    path("", views.index, name="index"),
    path("categories", views.categories, name="categories"),
    path("categories/<int:category_id>", views.category, name="category"),
    path("list", views.list, name="list"),
    path("listings/<int:auction_id>", views.listings, name="listings"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("watchlist/<int:user_id>", views.watchlist, name="watchlist"),
    # Helper views (functions)
    path("helper/listings/1/<int:auction_id>", views.helper_auction_state, name="helper_auction_state"),
    path("helper/listings/2/<int:auction_id>", views.helper_post_comment, name="helper_post_comment"),
    path("helper/listings/3/<int:auction_id>", views.helper_watchlist, name="helper_watchlist")
]