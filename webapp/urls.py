from django.urls import path
from . import views
from .views import browse_page,genre_page

urlpatterns = [
    path('home_page/', views.home_page, name='home_page'),
    path('about_page/', views.about_page, name='about_page'),
    path('save_registration/', views.save_registration, name='save_registration'),
    path('user_registration/', views.user_signup, name='user_registration'),
    path('', views.user_signin, name='user_signin'),
    path('login/', views.user_login, name='login'),
    path('user_logout/', views.user_logout, name='user_logout'),
    path('contact_page/', views.contact_page, name='contact_page'),
    path('save_contact/', views.save_contact, name='save_contact'),
    path('add_watchlist/', views.add_watchlist, name='add_watchlist'),
    path('watchlist/', views.watchlist, name='watchlist'),
    path('genre_page/', views.genre_page, name='genre_page'),
    path('browse_page/', views.browse_page, name='browse_page'),
    path("browse_page", browse_page, name="browse_page"),
    path("browse/", views.browse_page, name="browse"),
    path("watchlist/", views.watchlist, name="watchlist"),
    path("add-watchlist/<int:movie_id>/", views.add_watchlist, name="add_watchlist"),
    path("remove-watchlist/<int:movie_id>/", views.remove_watchlist, name="remove_watchlist"),
    path("movie/<int:movie_id>/", views.movie_detail, name="movie_detail"),
    path("search-movies/", views.search_movies, name="search_movies"),
    path("recommend/", views.tmdb_recommend_page, name="tmdb_recommend"),
    


]
