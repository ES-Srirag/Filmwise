from django.shortcuts import render, redirect
from adminapp.models import Movie, Genre
from adminapp import views
from webapp.models import RegistrationDb, ContactDb
from django.conf import settings
import requests
from .models import Watchlist
from django.http import JsonResponse
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd
from .tmdb_recommend import get_tmdb_recommendations
from django.contrib import messages
API_KEY = settings.TMDB_API_KEY


def home_page(request):
    API_KEY = settings.TMDB_API_KEY

    # Fetch Top Rated Movies
    top_rated_url = f"https://api.themoviedb.org/3/movie/top_rated?api_key={API_KEY}"
    top_rated_movies = requests.get(top_rated_url).json().get("results", [])

    # Fetch Trending Movies
    trending_url = f"https://api.themoviedb.org/3/trending/movie/day?api_key={API_KEY}"
    trending_movies = requests.get(trending_url).json().get("results", [])

    # Fetch Now Playing
    now_playing_url = f"https://api.themoviedb.org/3/movie/now_playing?api_key={API_KEY}"
    now_playing = requests.get(now_playing_url).json().get("results", [])

    # Fetch Genres from DB
    genres = Genre.objects.all()

    return render(request, "Home.html", {
        "genres": genres,
        "top_rated_movies": top_rated_movies,  
        "trending_movies": trending_movies,
        "now_playing": now_playing,
    })

def genre_page(request):
    API_KEY = settings.TMDB_API_KEY
    genre_id = request.GET.get("genre")

    movies = []

    if genre_id:
        for page in range(1, 6):
            url = (
                f"https://api.themoviedb.org/3/discover/movie"
                f"?api_key={API_KEY}"
                f"&with_genres={genre_id}"
                f"&sort_by=popularity.desc"
                f"&page={page}"
            )
            response = requests.get(url).json()
            movies.extend(response.get("results", []))

    return render(request, "Genre.html", {
        "movies": movies,
        "genre_id": genre_id,
    })



def about_page(request):
    genres = Genre.objects.all()
    return render(request, 'About.html', {'genres': genres})


def user_signup(request) :
    return render(request, 'Sign_up.html')

def user_signin(request) :
    return render(request, 'Sign_in.html')


def save_registration(request):
    if request.method == "POST":
        name = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirmPassword")

        if RegistrationDb.objects.filter(Name=name).exists():
            messages.warning(request, "Username already exists")
            return redirect(user_signup)

        elif RegistrationDb.objects.filter(Email=email).exists():
            messages.warning(request, "Email already registered")
            return redirect(user_signup)

        else:
            user = RegistrationDb(
                Name=name,
                Email=email,
                Password=password,
                Confirm_Password=confirm_password
            )
            user.save()
            messages.success(request, "Registration successful. Please login.")
            return redirect(user_login)

    messages.error(request, "Invalid request")
    return redirect('user_registration')

def user_login(request) :
    if request.method == "POST":
        name = request.POST.get("username")
        password = request.POST.get("password")
        if RegistrationDb.objects.filter(Name=name,Password=password).exists():
            request.session['Name']=name
            request.session['Password'] = password
            messages.success(request, "Login successful")
            return redirect(home_page)
        else:
            messages.error(request, "Invalid username or password")
            return redirect(user_signin)
    else:
        return redirect(user_signin)

def user_logout(request):
    del request.session['Name']
    del request.session['Password']
    messages.info(request, "You have been logged out")
    return redirect(home_page)

# Contact page
def save_contact(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        contact = request.POST.get('contact')
        subject = request.POST.get('subject')
        message = request.POST.get('message')

        ContactDb.objects.create(
            Name=name,
            Contact=contact,
            Subject=subject,
            Message=message
        )
        return redirect('contact_page')

    return render(request, 'Contact_us.html')

def contact_page(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        contact = request.POST.get('contact')
        subject = request.POST.get('subject')
        message = request.POST.get('message')

        ContactDb.objects.create(
            Name=name,
            Contact=contact,
            Subject=subject,
            Message=message
        )
        messages.success(request, "Your message has been sent successfully")
        return redirect('contact_page')

    return render(request, 'Contact_us.html')

# Add movie to watchlist
def add_watchlist(request, movie_id):
    uname = request.session.get('Name')

    if not uname:
        messages.warning(request, "Please login to add movies to your watchlist")
        return redirect('login')

    API_KEY = settings.TMDB_API_KEY
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={API_KEY}"

    response = requests.get(url).json()

    obj, created = Watchlist.objects.get_or_create(
        Username=uname,
        movie_id=movie_id,
        defaults={
            "title": response.get("title"),
            "poster_path": response.get("poster_path"),
            "rating": response.get("vote_average"),
        }
    )

    if created:
        messages.success(request, "Movie added to your watchlist")
    else:
        messages.info(request, "Movie already exists in your watchlist")

    return redirect("watchlist")



def remove_watchlist(request, movie_id):
    uname = request.session.get('Name')

    if not uname:
        messages.warning(request, "Please login to manage your watchlist")
        return redirect('login')

    deleted, _ = Watchlist.objects.filter(
        movie_id=movie_id,
        Username=uname
    ).delete()

    if deleted:
        messages.success(request, "Movie removed from your watchlist")
    else:
        messages.info(request, "Movie not found in your watchlist")

    return redirect("watchlist")



# View watchlist
def watchlist(request):
    uname = request.session.get('Name')

    if not uname:
        
        return redirect('login')

    API_KEY = settings.TMDB_API_KEY
    watch_items = Watchlist.objects.filter(Username=uname)

    movies = []
    error_message = ""

    for item in watch_items:
        url = f"https://api.themoviedb.org/3/movie/{item.movie_id}?api_key={API_KEY}"

        try:
            response = requests.get(url)
            response.raise_for_status()
            movie_data = response.json()
            movie_data["local_movie_id"] = item.movie_id
            movies.append(movie_data)
        except:
            movies.append(None)
            error_message = "Failed to fetch some movies."

    return render(request, "Watchlist.html", {
        "movies": movies,
        "error_message": error_message,
    })



#browse page
def browse_page(request):
    category = request.GET.get("category", "popular")
    search_query = request.GET.get("search", "")
    API_KEY = settings.TMDB_API_KEY
    base_url="https://api.themoviedb.org/3/movie/"
    error_message = ""
    if search_query:
        url = f"https://api.themoviedb.org/3/search/movie?api_key={API_KEY}&query={search_query}"
    else:
        url = f"{base_url}{category}?api_key={API_KEY}"
    try:    
        response = requests.get(url)
        response.raise_for_status()
        data = response.json().get('results',[])
    except Exception as e:
        data=[]
        error_message= f"Something went wrong!"
    print(data)
    return render(request, "Browse.html", {"movies":data, "category":category,
                                                   "search_query":search_query,
                                                   "error_message":error_message})

#movie detail
def movie_detail(request, movie_id):
    API_KEY = settings.TMDB_API_KEY

    movie_url = f"https://api.themoviedb.org/3/movie/{movie_id}"
    credits_url = f"https://api.themoviedb.org/3/movie/{movie_id}/credits"
    videos_url = f"https://api.themoviedb.org/3/movie/{movie_id}/videos"
    similar_url = f"https://api.themoviedb.org/3/movie/{movie_id}/similar"

    params = {"api_key": API_KEY}

    try:
        movie = requests.get(movie_url, params=params).json()
        credits = requests.get(credits_url, params=params).json()
        videos = requests.get(videos_url, params=params).json()
        similar = requests.get(similar_url, params=params).json()

        cast = credits.get("cast", [])
        trailers = [
            v for v in videos.get("results", [])
            if v["type"] == "Trailer" and v["site"] == "YouTube"
        ]

        similar_movies = similar.get("results", [])

    except Exception as e:
        movie = None
        cast = []
        trailers = []
        similar_movies = []

    context = {
        "movie": movie,
        "cast": cast,
        "trailers": trailers,
        "similar_movies": similar_movies,
    }

    return render(request, "MovieDetail.html", context)

def search_movies(request):
    query = request.GET.get('q', '').strip()
    if not query:
        return JsonResponse({'results': []})

    API_KEY = settings.TMDB_API_KEY  

    url = f"https://api.themoviedb.org/3/search/movie?api_key={API_KEY}&query={query}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json().get("results", [])

        # Return only titles for the suggestions
        titles = [movie["title"] for movie in data[:10]]
        return JsonResponse({'results': titles})

    except Exception as e:
        print("TMDB API error:", e)
        return JsonResponse({'results': []})

def fetch_tmdb_movie(title):
    url = "https://api.themoviedb.org/3/search/movie"
    params = {
        "api_key": settings.TMDB_API_KEY,
        "query": title
    }
    data = requests.get(url, params=params).json()
    results = data.get("results", [])

    if results:
        return results[0]  
    return None


def tmdb_recommend_page(request):
    movie_name = request.GET.get("movie", "").strip()
    movies = []
    API_KEY = settings.TMDB_API_KEY

    if movie_name:
        recommended_titles = get_tmdb_recommendations(movie_name, limit=12)

        for title in recommended_titles:
            url = f"https://api.themoviedb.org/3/search/movie?api_key={API_KEY}&query={title}"
            try:
                response = requests.get(url).json()
                results = response.get("results", [])
                if results:
                    movies.append(results[0])  
            except:
                continue

    return render(request, "TMDB_Recommendations.html", {
        "movie_name": movie_name,
        "movies": movies
    })
