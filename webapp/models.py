from django.db import models

# Create your models here.

# User registration
class RegistrationDb(models.Model):
    Name = models.CharField(max_length=100, null=True, blank=True)
    Password = models.CharField(max_length=100, null=True, blank=True)
    Confirm_Password = models.CharField(max_length=100, null=True, blank=True)
    Email = models.EmailField(max_length=100, null=True, blank=True)

# Contact form
class ContactDb(models.Model):
    Name = models.CharField(max_length=100, null=True, blank=True)
    Contact = models.EmailField(max_length=100, null=True, blank=True)
    Subject = models.CharField(max_length=100, null=True, blank=True)
    Message = models.CharField(max_length=500, null=True, blank=True)

# Watchlist
class Watchlist(models.Model):
    Username = models.CharField(max_length=100, null=True, blank=True)
    movie_id = models.IntegerField()
    title = models.CharField(max_length=255)
    poster_path = models.CharField(max_length=255, blank=True, null=True)
    rating = models.FloatField(null=True, blank=True)

# Genre
class Genre(models.Model):
    name = models.CharField(max_length=100)
    icon = models.CharField(max_length=100, null=True, blank=True)  
