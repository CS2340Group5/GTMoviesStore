from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator

# Create your models here.
class Movie(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    price = models.IntegerField()
    description = models.TextField()
    image = models.ImageField(upload_to='movie_images/')
    def __str__(self):
        return str(self.id) + ' - ' + self.name

class Review(models.Model):
    id = models.AutoField(primary_key=True)
    comment = models.CharField(max_length=255, blank=True)
    date = models.DateTimeField(auto_now_add=True)
    rating = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(5)], blank=True, default=0)
    movie = models.ForeignKey(Movie,
        on_delete=models.CASCADE)
    user = models.ForeignKey(User,
        on_delete=models.CASCADE)
    def __str__(self):
        return f"{self.id} - {self.user.username} - {self.movie.name} - {self.rating}"

class Report(models.Model):
    id = models.AutoField(primary_key=True)
    date = models.DateTimeField(auto_now_add=True)
    review = models.ForeignKey(Review, 
            on_delete=models.CASCADE)
    def __str__(self):
        return f"{self.id} - Review: {self.review.id}"
