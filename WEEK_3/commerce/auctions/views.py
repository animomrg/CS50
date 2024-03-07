from decimal import Decimal, InvalidOperation
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.db.models import Max
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse


from .models import User, Listing, Bid, Comment, Watchlist, Category


def active_listings(request):
    """View for main landing page"""
    listings = Listing.objects.filter(is_active=True)
    return render(request, "auctions/active_listings.html", {'listings': listings})

def login_view(request):
    """View for login"""
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("active_listings"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    """View for logout"""
    logout(request)
    return HttpResponseRedirect(reverse("active_listings"))


def register(request):
    """View for registration to the platform"""
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
        return HttpResponseRedirect(reverse("active_listings"))
    else:
        return render(request, "auctions/register.html")


@login_required
def new_listing(request):
    """View for creating a new listing"""
    if request.method == "POST":
        # Process the form data
        title = request.POST.get('title')
        description = request.POST.get('description')
        starting_bid = request.POST.get('starting_bid')
        buy_it_now_price = request.POST.get('buy_it_now_price')
        image_url = request.POST.get('image_url')
        category = request.POST.get('category')

        # Create and save the new listing object
        new_listing = Listing(
            title=title,
            description=description,
            starting_bid=starting_bid,
            buy_it_now_price=buy_it_now_price,
            image_url=image_url,
            category=category,
            created_by=request.user
        )
        new_listing.save()

        # Redirect to a new URL, for example, the listing detail view
        return redirect(reverse('listing_detail', args=[new_listing.id]))

    # If a GET (or any other method) we'll create a blank form  
    category_choices = Listing.CATEGORY_CHOICES
    return render(request, 'auctions/new_listing.html', {'category_choices': category_choices})


def listing_detail(request, listing_id):
    """View for a specific item listing"""
    listing = get_object_or_404(Listing, pk=listing_id)
    on_watchlist = False
    if request.user.is_authenticated:
        on_watchlist = Watchlist.objects.filter(user=request.user, listing=listing).exists()

    if request.method == "POST":
        if 'toggle_watchlist' in request.POST:
            if on_watchlist:
                Watchlist.objects.get(user=request.user, listing=listing).delete()
            else:
                Watchlist.objects.create(user=request.user, listing=listing)
            return HttpResponseRedirect(reverse('listing_detail', args=[listing_id]))
        
        if 'post_comment' in request.POST:
            comment_text = request.POST.get('comment', '').strip()

            # Check if the comment is not empty
            if not comment_text:
                # Return an error message or redirect as appropriate
                return HttpResponse("Comment cannot be blank.", status=400)

            # If the comment is valid, save it
            Comment.objects.create(user=request.user, listing=listing, comment=comment_text)
            return redirect(reverse('listing_detail', args=[listing_id]))
        
        if 'place_bid' in request.POST:
            bid_amount_str = request.POST.get('bid_amount', '').strip()
        
            # Attempt to convert the bid amount to Decimal, handling both integer and decimal strings
            try:
                bid_amount = Decimal(bid_amount_str)
            except InvalidOperation:
                return HttpResponse("Invalid bid amount.", status=400)
            
            # Ensure the bid amount is a minimum increment over the current or starting bid
            current_highest_bid = listing.current_price or listing.starting_bid
            if bid_amount <= current_highest_bid:
                return HttpResponse("Your bid must be higher than the current highest bid.", status=400)
            
            # Save the new bid
            Bid.objects.create(user=request.user, listing=listing, bid_amount=bid_amount)
            listing.current_price = bid_amount  # Update the listing's current price
            listing.save()
            
            return redirect('listing_detail', listing_id=listing_id)
        
        if 'buy_now' in request.POST:
            # Handle the buy now action
            listing.is_active = False
            listing.winner = request.user  # Assuming you have a winner field to store the buyer
            listing.save()
            return redirect(reverse('listing_detail', args=[listing_id]))
        
        if 'close_auction' in request.POST and listing.created_by == request.user:
            # Handle the close auction action
            listing.is_active = False
            # Determine the winner based on the highest bid
            highest_bid = listing.bids.order_by('-bid_amount').first()
            if highest_bid:
                listing.winner = highest_bid.user
            listing.save()
            return redirect(reverse('listing_detail', args=[listing_id]))

    return render(request, 'auctions/listing_detail.html', {
        'listing': listing,
        'on_watchlist': on_watchlist,
        # Include other context variables as needed
    })

@login_required
def user_watchlist(request):
    # Fetch all watchlist items for the current user
    watchlist_items = Watchlist.objects.filter(user=request.user).select_related('listing')
    # Pass the watchlist items to the template
    return render(request, 'auctions/watchlist.html', {'watchlist_items': watchlist_items})

def view_categories(request):
    categories = Category.objects.all()
    return render(request, 'auctions/view_categories.html', {'categories': categories})

def category_items(request, category_id):
    category = get_object_or_404(Category, pk=category_id)
    listings = Listing.objects.filter(category=category, is_active=True)  # Assuming an 'is_active' field to filter active listings
    return render(request, 'auctions/category_items.html', {'category': category, 'listings': listings})