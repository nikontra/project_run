from django.contrib import admin

from app_run.models import Run, Challenge, AthleteInfo

# Register your models here.
admin.site.register(Run)
admin.site.register(Challenge)
admin.site.register(AthleteInfo)