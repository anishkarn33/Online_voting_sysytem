from django.contrib.auth.models import AbstractUser
from django.db import models
import random
import string


class User(AbstractUser):
    USER_TYPE_VOTER = 'voter'
    USER_TYPE_CANDIDATE = 'candidate'
    USER_TYPE_ADMIN = 'admin'

    USER_TYPE_CHOICES = (
        (USER_TYPE_VOTER, 'Voter'),
        (USER_TYPE_CANDIDATE, 'Candidate'),
        (USER_TYPE_ADMIN, 'Admin'),
    )

    user_type = models.CharField(
        max_length=20, choices=USER_TYPE_CHOICES, default=USER_TYPE_VOTER)
    
    voter_id = models.CharField(max_length=200, null=True, blank=True)

    def save(self, *args, **kwargs):
        if self.user_type == self.USER_TYPE_VOTER and not self.voter_id:
            # Use first name or part of the username if the first name is not available
            name_part = self.first_name if self.first_name else self.username.split('@')[0]
            name_part = name_part[:4].ljust(4, '0')  # Ensure it's at least 4 chars long, pad with '0' if necessary

            # Generate a random four-digit number
            number_part = ''.join(random.choices(string.digits, k=4))

            # Combine and shuffle to form voter_id
            combined = list(name_part + number_part)
            random.shuffle(combined)
            self.voter_id = ''.join(combined)

        super().save(*args, **kwargs)


class Election(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class ElectionCandidate(models.Model):
    election = models.ForeignKey(Election, on_delete=models.CASCADE, related_name='candidates')
    candidate = models.ForeignKey(User, on_delete=models.CASCADE, related_name='elections')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class ElectionVoter(models.Model):
    election = models.ForeignKey(
        Election, on_delete=models.CASCADE, related_name='voters')
    voter = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='elections_voted')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class ElectionAdmin(models.Model):
    election = models.ForeignKey(
        Election, on_delete=models.CASCADE, related_name='admins')
    admin = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='elections_admin')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Vote(models.Model):
    voter = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='votes')
    election = models.ForeignKey(
        Election, on_delete=models.CASCADE, related_name='votes')
    candidate = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='votes_received')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class ElectionResult(models.Model):
    election = models.ForeignKey(
        Election, on_delete=models.CASCADE, related_name='results')
    candidate = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='results')
    vote_count = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)



