from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    def __str__(self):
    	return "{}".format(self.username)

category_choices = [
		('Fashion', 'Fashion'),
		('Toys', 'Toys'),
		('Home', 'Home'),
		('Electronics', 'Electronics'),
		('Bike', 'Bike'),
		('Car', 'Car'),
		('Furniture', 'Furniture'),
		('Computer', 'Computer'),
	]

class Listing(models.Model):
	user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='listings')
	title = models.CharField(max_length=128)
	active = models.BooleanField(default=True)
	description = models.TextField()
	bid = models.IntegerField()
	datetime = models.DateTimeField(auto_now_add=True)
	imageurl = models.URLField(blank=True)
	category = models.CharField(blank=True, choices=category_choices, max_length=128)
	watchlist = models.ManyToManyField(User, blank=True, related_name='watchlist')
	buyer = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True, related_name='purchases')

	def __str__(self):
		return "{}: {}".format(self.user.username, self.title)

class Bids(models.Model):
	listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name='bids')
	user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bids')
	bid = models.IntegerField()
	datetime = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return "{} : {} : {}".format(self.user.username, self.listing.title, self.bid)

class Comments(models.Model):
	listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name='comments')
	user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
	comment = models.TextField()
	datetime = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return "{} : {}".format(self.user.username, self.listing.title)



		

