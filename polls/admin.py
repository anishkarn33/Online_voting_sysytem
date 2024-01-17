from django.contrib import admin
from .models import *


admin.site.register(User)
admin.site.register(Election)
admin.site.register(ElectionCandidate)
admin.site.register(ElectionVoter)
admin.site.register(ElectionAdmin)
admin.site.register(Vote)
admin.site.register(ElectionResult)