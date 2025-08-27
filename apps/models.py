from django.db import models


# Create your models here.

class Service(models.Model):
    Service_type = models.CharField(max_length=255)
    image = models.CharField(max_length=255, blank=True, null=True)  
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.Service_type

    # Kwa Open Graph preview (Facebook, WhatsApp etc.)
    def get_og_image_url(self):
        if self.image:
            return f"https://ucarecdn.com/{self.image}/-/resize/1200x630/-/format/auto/"
        return ''

    # Kwa matumizi ya kawaida kwenye site (speed optimized)
    def get_image_url(self):
        if self.image:
            return f"https://ucarecdn.com/{self.image}/-/format/jpg/-/quality/smart/"
        return ''



class Question(models.Model):
    question = models.CharField(max_length=500)
    answer = models.TextField()

    
    def __str__(self):
        return self.question

class Team(models.Model):
    full_name = models.CharField(max_length=255)
    image = models.CharField(max_length=255, blank=True, null=True)  # Hifadhi Uploadcare UUID au URL
    position = models.CharField(max_length=255)
    facebook_link = models.URLField(max_length=300, blank=True, null=True)
    twitter_link = models.URLField(max_length=300, blank=True, null=True)
    instagram_link = models.URLField(max_length=300, blank=True, null=True)
    linkedIn = models.URLField(max_length=300, blank=True, null=True)
    
    def __str__(self):
        return self.full_name

    # Kwa Open Graph preview (Facebook, WhatsApp etc.)
    def get_og_image_url(self):
        if self.image:
            return f"https://ucarecdn.com/{self.image}/-/resize/1200x630/-/format/auto/"
        return ''

    # Kwa matumizi ya kawaida kwenye site (speed optimized)
    def get_image_url(self):
        if self.image:
            return f"https://ucarecdn.com/{self.image}/-/format/jpg/-/quality/smart/"
        return ''


    
class Contact(models.Model):
    full_name = models.CharField(max_length=255)
    email = models.EmailField()
    subject = models.CharField(max_length=500)
    message = models.TextField()

    def __str__(self):
        return self.full_name



from django.contrib.auth.models import User

class WebsiteType(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, blank=True)
    
    def __str__(self):
        return self.name

class Client(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)
    company = models.CharField(max_length=100, blank=True)
    
    def __str__(self):
        return self.name

class ProjectProposal(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    website_type = models.ForeignKey(WebsiteType, on_delete=models.CASCADE)
    requirements = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    pdf_file = models.URLField(blank=True)  
    
    def __str__(self):
        return f"{self.client.name} - {self.website_type.name}"