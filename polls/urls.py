from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('candidates/', views.candidates, name='candidates'),
    path('elections/', views.elections, name='elections'),
    path('elections/<int:election_id>/vote/',
         views.election_vote, name='election_vote'),
    path('elections/<int:election_id>/vote/<int:candidate_id>/',
         views.vote, name='vote'),
    path('elections/<int:election_id>/register/',
         views.election_voter_register, name='election_voter_register'),
    path('elections/<int:election_id>/register/candidate/',
         views.election_candidate_register, name='election_candidate_register'),
    path('elections/<int:election_id>/close/',
         views.election_close, name='election_close'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('', views.index_view, name='index'),
    path('result/', views.show_results, name='result'),
    path('elections/<int:election_id>/vote/<int:candidate_id>/',
         views.vote, name='vote')
]
