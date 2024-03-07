from django.urls import path

from . import views

urlpatterns = [
    path("", views.active_listings, name="active_listings"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("new_listing", views.new_listing, name="new_listing"),
    path("listing/<int:listing_id>/", views.listing_detail, name='listing_detail'),
    path('watchlist/', views.user_watchlist, name='user_watchlist'),
    path('categories/', views.view_categories, name='view_categories'),
    path('categories/<int:category_id>/', views.category_items, name='category_items'),  # Assuming you're using the category ID
]
