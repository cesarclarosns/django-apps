from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from .forms import AuctionForm, BidForm, CommentForm
from .models import Auction, Bid, Category, Comment, User


""" Views """

def categories(request):
    # Get all categories
    categories = Category.objects.all().order_by('category')
    return render(request, "auctions/categories.html", {
        "categories": categories
    })


def category(request, category_id):
    # Get all listings related to a category
    category = Category.objects.get(pk=category_id)
    listings = category.auction_set.all()
    return render(request, "auctions/category.html", {
        "category": category, 
        "listings": listings
    })
    

def index(request):
    # Get all auctions with a state=True and order them by pub_date
    return render(request, "auctions/index.html", {
        "auctions": Auction.objects.filter(state=True).order_by('-pub_date')
    })


def list(request):
    if request.method == "POST":
        
        # Create new auction and new bid
        auction_form = AuctionForm(request.POST)
        bid_form = BidForm(request.POST)
        if auction_form.is_valid() and bid_form.is_valid():
        
            # Create new auction
            new_auction = auction_form.save(commit=False)
            new_auction.user = request.user
            new_auction.save()
                    
            # Create new bid
            new_bid = bid_form.save(commit=False)
            new_bid.auction = new_auction
            new_bid.user = request.user
            new_bid.save()
            
            return HttpResponseRedirect(reverse("auctions:index"))
        else:
            # Return the submited form
            return render(request, "auctions/list.html", {
                "auction_form": auction_form, 
                "bid_form": bid_form
            })

    else:
        return render(request, "auctions/list.html", {
            "auction_form": AuctionForm(),
            "bid_form": BidForm()
        })


def listings(request, auction_id):
    error_messages = []
    listing = Auction.objects.get(pk=auction_id)
    user_watchlist = None
    if request.user.is_authenticated:
        user_watchlist = User.objects.get(pk=request.user.id).watchlist.all()
    
    if request.method == "POST":
        bid_form = BidForm(request.POST)      
        # Validate the bid_form  
        if bid_form.is_valid():
            new_bid = bid_form.save(commit=False)
            if listing.bids_number() == 1:
                if new_bid.amount >= listing.current_bid().amount:
                    new_bid.user = request.user
                    new_bid.auction = listing
                    new_bid.save()
                    return HttpResponseRedirect(reverse("auctions:listings", args=[auction_id]))
                else:
                    error_messages.append("Your bid must be at least equal to the starting bid!")
            else:
                if new_bid.amount >= listing.current_bid().amount:
                    new_bid.user = request.user
                    new_bid.auction = listing
                    new_bid.save()
                    return HttpResponseRedirect(reverse("auctions:listings", args=[auction_id]))
                else:
                    error_messages.append("Your bid must be higher than the current bid!")

    return render(request, "auctions/listings.html", {
        "bid_form": BidForm(),
        "comment_form": CommentForm(),
        "comments": listing.comments.order_by('-pub_date'),
        "error_messages": error_messages,
        "listing": listing,
        "user_watchlist": user_watchlist
    })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("auctions:index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("auctions:index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("auctions:index"))
    else:
        return render(request, "auctions/register.html")


@login_required(login_url="/login/")
def watchlist(request, user_id):
    user_watchlist = User.objects.get(pk=request.user.id).watchlist.all()
    
    return render(request, "auctions/watchlist.html", {
        "user_watchlist": user_watchlist
    })
    

""" Helper functions """

def helper_auction_state(request, auction_id):
    """
    Close or reopen an auction
    """
    auction = Auction.objects.get(pk=auction_id)
    auction.state = not auction.state
    auction.save()
    
    return HttpResponseRedirect(reverse("auctions:listings", args=[auction_id]))

        
def helper_post_comment(request, auction_id):
    """
    Post comment
    """
    if request.method == "POST":
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            new_comment = comment_form.save(commit=False)
            new_comment.auction = Auction.objects.get(pk=auction_id)
            new_comment.user = request.user
            new_comment.save()
    return HttpResponseRedirect(reverse("auctions:listings", args=[auction_id]))


def helper_watchlist(request, auction_id):
    """
    Add or remove auction from watchlist
    """
    watchlist = User.objects.get(pk=request.user.id).watchlist
    auction = Auction.objects.get(pk=auction_id)
    if auction in watchlist.all():
        watchlist.remove(auction)
    else:
        watchlist.add(auction)
    return HttpResponseRedirect(reverse("auctions:listings", args=[auction_id]))
        



    