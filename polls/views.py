from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.db.models import Count, Q
from django.utils import timezone
from .forms import LoginForm, RegisterForm
from .models import *
from .decorators import voter_required, candidate_required, admin_required

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
def candidates(request):
    candidates_users = User.objects.filter(user_type=User.USER_TYPE_CANDIDATE)

    current_user = request.user

    return render(request, 'candidates.html', {
        'candidates': candidates_users,
        'user': current_user
    })

@login_required(login_url='/login/')
def elections(request):
    elections = Election.objects.all().annotate(
        candidates_count=Count('candidates'),
        voters_count=Count('voters'),
        votes_count=Count('votes'),
        is_voted=Count('votes', filter=Q(votes__voter=request.user)),
        is_allowed_to_vote=Count('voters', filter=Q(voters__voter=request.user)),
        is_candidate=Count('candidates', filter=Q(candidates__candidate=request.user)),
    ).filter(
        Q(start_date__lte=timezone.now()) & Q(end_date__gte=timezone.now())
    )
    current_user = request.user

    return render(request, 'elections.html', {
        'elections': elections,
        'user': current_user
    })


@login_required(login_url='/login/')
def election_vote(request, election_id):
    election = Election.objects.filter(id=election_id).first()

    # check if the election exists and active by dates
    if not election:
        return redirect('elections')
    
    if not (election.start_date <= timezone.now() <= election.end_date):
        return redirect('elections')

    # check if the user is allowed to vote
    if not ElectionVoter.objects.filter(election=election, voter=request.user).exists():
        return redirect('elections')
    
    # check if the user has already voted
    if Vote.objects.filter(election=election, voter=request.user).exists():
        return redirect('elections')

    election_candidates = ElectionCandidate.objects.filter(election=election)


    current_user = request.user

    return render(request, 'election_vote.html', {
        'election': election,
        'candidates': election_candidates,
        'user': current_user
    })

# election voter register
@login_required(login_url='/login/')
@voter_required
def election_voter_register(request, election_id):
    if request.method == 'POST':
        election = Election.objects.filter(id=election_id).first()

        if not election:
            return redirect('elections')

        # check if the user is already registered
        if ElectionVoter.objects.filter(election=election, voter=request.user).exists():
            return redirect('elections', election_id=election_id)

        # register the user
        ElectionVoter.objects.create(
            election=election,
            voter=request.user
        )

        return redirect('election_vote', election_id=election_id)
    else:
        return redirect('elections', election_id=election_id)


# election candidate register
@login_required(login_url='/login/')
@candidate_required
def election_candidate_register(request, election_id):
    if request.method == 'POST':
        election = Election.objects.filter(id=election_id).first()

        if not election:
            return redirect('elections')

        # check if the user is already registered
        if ElectionCandidate.objects.filter(election=election, candidate=request.user).exists():
            return redirect('elections')

        # register the user
        ElectionCandidate.objects.create(
            election=election,
            candidate=request.user
        )

        return redirect('elections')
    else:
        return redirect('elections')

# vote view
@login_required(login_url='/login/')
@voter_required
def vote(request, election_id, candidate_id):
    if request.method == 'POST':
        election = Election.objects.filter(id=election_id).first()
        candidate = User.objects.filter(id=candidate_id).first()

        if not election:
            return redirect('elections')

        if not candidate:
            return redirect('election_vote', election_id=election_id)

        # check if the user has already voted
        if Vote.objects.filter(election=election, voter=request.user).exists():
            return redirect('election_vote', election_id=election_id)

        # check if the user is allowed to vote
        if not ElectionVoter.objects.filter(election=election, voter=request.user).exists():
            return redirect('election_vote', election_id=election_id)

        # create a vote
        vote = Vote.objects.create(
            election=election,
            voter=request.user,
            candidate=candidate
        )

        # TODO: create a result
        # result = ElectionResult.objects.filter(
        #     election=election, candidate=candidate).first()
        # if result:
        #     result.vote_count += 1
        #     result.save()
        # else:
        #     ElectionResult.objects.create(
        #         election=election,
        #         candidate=candidate,
        #         vote_count=1
        #     )

        return redirect('elections')
    else:
        return redirect('election_vote', election_id=election_id)

@login_required(login_url='/login/')
def logout_view(request):
    logout(request)
    return redirect('login')

def show_results(request):
    # Retrieve all election results from the database
    results = ElectionResult.objects.all()
    # Pass the results to the template for rendering
    return render(request, 'result.html', {'results': results})

def vote(request, election_id, candidate_id):
    if request.method == 'POST':
        return redirect('elections')  # Redirect to the elections page or any other appropriate page
    else:
        return redirect('elections')