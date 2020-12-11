from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth.decorators import login_required

from django.forms import modelform_factory
from .models import User, Listing, Bids, Comments, category_choices

### Forms ###
ListingForm = modelform_factory(Listing, fields=('title', 'description', 'bid', 'category', 'imageurl'))
BidForm = modelform_factory(Bids, fields=('bid',))
CommentForm = modelform_factory(Comments, fields=('comment',))


def index(request):
    lstings = Listing.objects.filter(active=True).order_by('-datetime')
    if len(lstings)>0:
        return render(request, "auctions/index.html", {
            "lstings": lstings,
            })
    else:
        return render(request, "auctions/index.html", {
            "message": "No active listing present."
            })


def login_view(request):
    next = ''
    if request.GET:
        next = request.GET['next']
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            if next:
                return HttpResponseRedirect(next)
            else:
                return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


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
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")




@login_required(login_url='/login')
def createlisting(request):
    if request.method == "POST":
        form = ListingForm(request.POST)
        try:    
            if form.is_valid():
                Listing.objects.create(
                    user=request.user,
                    title=form.cleaned_data['title'],
                    description=form.cleaned_data['description'],
                    bid=form.cleaned_data['bid'],
                    imageurl=form.cleaned_data['imageurl'],
                    category=form.cleaned_data['category'])
                return render(request, "auctions/successfull.html", {
                    "message": "Listing created successfully.",
                    })
        except:
            form = ListingForm()
            return render(request, "auctions/newlisting.html", {
                "message": "Please enter the details correctly.",
                "form": form,
                })
    form = ListingForm()
    return render(request, "auctions/newlisting.html", {
        "form": form,
        })



def listing(request, listing_id):
    lst = Listing.objects.get(id=listing_id)
    if lst:
        cmnts = lst.comments.all().order_by('-datetime')
        bform = BidForm()
        cform = CommentForm()
        return render(request, "auctions/listing.html", {
            "lst": lst,
            "cmnts": cmnts,
            "bform": bform,
            "cform": cform,
            })
    else:
        return render(request, "auctions/listing.html", {
            "message": "Listing not present."
            })



@login_required(login_url="/login")
def bid(request, listing_id):
    lst = Listing.objects.get(id=listing_id)
    cmnts = lst.comments.all().order_by('-datetime')
    cform = CommentForm()
    if request.method=='POST':
        try:
            bform = BidForm(request.POST)
            if bform.is_valid():
                if bform.cleaned_data['bid']>lst.bid:
                    lst.bid=bform.cleaned_data['bid']
                    lst.buyer=request.user
                    lst.save(update_fields=['bid','buyer'])
                    Bids.objects.create(
                        listing=lst,
                        user=request.user,
                        bid=bform.cleaned_data['bid']
                        )
                    return render(request, "auctions/successfull.html", {
                        "message": "Bid placed successfully.",
                        })
                else:
                    return render(request, "auctions/listing.html", {
                        "lst": lst,
                        "cmnts": cmnts,
                        "cform": cform,
                        "bform": bform,
                        "bid_error_message": "Please place bid greater than {}".format(lst.bid),
                        })
        except Exception as e:
            bform = BidForm()
            return render(request, "auctions/listing.html", {
                "lst": lst,
                "cmnts": cmnts,
                "cform": cform,
                "bform": bform,
                "bid_error_message": "Please enter only positive interger values greater than {}.".format(lst.bid),
                })
    return HttpResponseRedirect(reverse("listing", args=[listing_id,]))



@login_required(login_url="/login")
def comment(request, listing_id):
    lst = Listing.objects.get(id=listing_id)
    if request.method=='POST':
        try:
            cform = CommentForm(request.POST)
            if cform.is_valid():
                Comments.objects.create(
                    listing=lst,
                    user=request.user,
                    comment=cform.cleaned_data['comment']
                    )
                return HttpResponseRedirect(reverse('listing', args=[listing_id,]))
        except:
            return HttpResponseRedirect(reverse('listing', args=[listing_id,]))
    else:
        return HttpResponseRedirect(reverse('listing', args=[listing_id,]))


@login_required(login_url='/login')
def watchlist(request, listing_id):
    lst = Listing.objects.get(id=listing_id)
    if request.method=="POST":
        if request.user in lst.watchlist.all():
            lst.watchlist.remove(request.user)
        else:
            lst.watchlist.add(request.user)
    return HttpResponseRedirect(reverse('listing', args=[listing_id,]))


@login_required(login_url='/login')
def close(request, listing_id):
    lst = Listing.objects.get(id=listing_id)
    if request.method=="POST":
        lst.active=False
        lst.save(update_fields=['active'])
    return HttpResponseRedirect(reverse('listing', args=[listing_id,]))


@login_required(login_url='/login')
def userwatchlist(request):
    user = request.user
    lstings = user.watchlist.all().order_by('-datetime')
    return render(request, "auctions/watchlist.html", {
        "lstings": lstings,
        })


@login_required(login_url='/login')
def purchases(request):
    user = request.user
    lstings = user.purchases.filter(active=False).order_by('-datetime')
    return render(request, "auctions/purchases.html", {
        "lstings": lstings,
        })


@login_required(login_url='/login')
def userbids(request):
    user = request.user
    bids = Bids.objects.filter(user=user)
    return render(request, "auctions/bids.html", {
        "bids": bids,
        })



def categories(request):
    categories = [c[0] for c in category_choices]
    categories.sort()
    return render(request, "auctions/categories.html", {
        "categories": categories,
        })



def category(request, category):
    lstings = Listing.objects.filter(category=category, active=True).order_by('-datetime')
    return render(request, "auctions/category.html", {
        "lstings": lstings,
        "category": category,
        })


@login_required(login_url='/login')
def mylistings(request):
    lstings = Listing.objects.filter(user=request.user).order_by('-datetime')
    return render(request, "auctions/mylistings.html", {
        "lstings": lstings,
        })