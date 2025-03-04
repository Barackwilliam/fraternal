from django.shortcuts import render
from .models import Question,Service,Team
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User, auth
from django.contrib.auth.decorators import login_required
from .forms import MyContact


# Home Page
def home(request):
    team = Team.objects.all()

    context = {
        'team':team
    }
    return render(request, 'index.html',context)

# Elimu ya Ufahamu
def service(request):
    services = Service.objects.all()
    questions = Question.objects.all()

    context = {
        'services':services,
        'questions':questions

    }

    return render(request, 'service.html',context)

# Warsha za Kiroho
def contact(request):
    return render(request, 'contact.html')

# Ushuhuda wa Wateja
def About(request):
    return render(request, 'about.html')


# Warsha za Kiroho
def contact(request):
    form = MyContact(request.POST)
    ujumbe = ""


    if request.method == 'POST':
        form = MyContact(request.POST)
        if form.is_valid():
            form.save()
            ujumbe = "Hongera Ujumbe Wako Umetumwa Kikamilifu"
        else:
            form = MyContact()  
      
    context = {
        'form':form,
        'ujumbe':ujumbe
    }
    return render(request, 'contact.html',context)

