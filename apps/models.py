from django.db import models
from cloudinary.models import CloudinaryField

# Create your models here.

class Service(models.Model):
    Service_type = models.CharField(max_length=255)
    image = CloudinaryField('image')
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.Service_type


class Question(models.Model):
    question = models.CharField(max_length=500)
    answer = models.TextField()

    
    def __str__(self):
        return self.question

class Team(models.Model):
    full_name = models.CharField(max_length=255)
    image = image = CloudinaryField('image')
    position = models.CharField(max_length=255)
    facebook_link = models.URLField(max_length=300, blank=True, null=True)
    twitter_link = models.URLField(max_length=300, blank=True, null=True)
    instagram_link = models.URLField(max_length=300, blank=True, null=True)
    linkedIn = models.URLField(max_length=300, blank=True, null=True)
    
    def __str__(self):
        return self.full_name

    
class Contact(models.Model):
    full_name = models.CharField(max_length=255)
    email = models.EmailField()
    subject = models.CharField(max_length=500)
    message = models.TextField()

    def __str__(self):
        return self.full_name