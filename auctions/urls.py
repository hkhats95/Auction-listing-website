from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path('listing/<int:listing_id>', views.listing, name='listing'),
    path('<int:listing_id>/bid', views.bid, name='bid'),
    path('<int:listing_id>/comment', views.comment, name='comment'),
    path('createlisting', views.createlisting, name='createlisting'),
    path('<int:listing_id>/watchlist',views.watchlist, name='watchlist'),
    path('<int:listing_id>/close', views.close, name='close'),
    path('watchlist', views.userwatchlist, name='userwatchlist'),
    path('purchases', views.purchases, name='purchases'),
    path('bids', views.userbids, name='userbids'),
    path('categories', views.categories, name='categories'),
    path('categories/<str:category>', views.category, name='category'),
    path('mylistings', views.mylistings, name='mylistings'),

]
