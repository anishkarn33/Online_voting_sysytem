from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from .forms import LoginForm, RegisterForm
from .models import *


def index_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    else:
        return redirect('login')


def login_view(request):
    # Check if the user is already authenticated
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            # Invalid login
            form = LoginForm()
            return render(request, 'login.html', {'error': 'Invalid credentials', 'form': form})
    else:
        form = LoginForm()

    return render(request, 'login.html', {'form': form})


def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Log the user in
            login(request, user)
            return redirect('dashboard')
        else:
            form_errors = form.errors.as_data()
            # get first error message
            form_errors = form_errors[list(form_errors.keys())[0]][0].message
            return render(request, 'register.html', {'form': form, 'error': form_errors})
    else:
        form = RegisterForm()

    return render(request, 'register.html', {'form': form})


@login_required(login_url='/login/')
def dashboard(request):
    total_elections = Election.objects.count()
    total_candidates = ElectionCandidate.objects.count()
    total_voters = ElectionVoter.objects.count()
    total_votes = Vote.objects.count()

    current_user = request.user

    return render(request, 'dashboard.html', {
        'total_elections': total_elections,
        'total_candidates': total_candidates,
        'total_voters': total_voters,
        'total_votes': total_votes,
        'user': current_user
    })


@login_required(login_url='/login/')
def logout_view(request):
    logout(request)
    return redirect('login')
