from django.db import models

# Create your models here.

# GENRE
class Genre(models.Model):
    genre_name = models.CharField(max_length=100, null=True, blank=True)
    description = models.TextField(null=True, blank=True)


# MOVIE
from django.db import models

class Movie(models.Model):
    title = models.CharField(max_length=150,null=True, blank=True)
    genre = models.CharField(max_length=100, null=True, blank=True)
    release_year = models.IntegerField(null=True)
    description = models.TextField(null=True, blank=True)
    poster = models.ImageField(upload_to='movie_posters/', null=True, blank=True)


