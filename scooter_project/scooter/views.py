from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Scooter

@login_required
def index(request):
    scooters = Scooter.objects.filter(is_available=True).order_by('name')

    return render(request, 'index.html', {
        'username': request.user.username,
        'scooters': scooters,
    })