from django.db import models

from apps.core.models import TimeStampedModel


class TravelProject(TimeStampedModel):
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='projects')
    name = models.CharField(max_length=200)
    description = models.TextField()
    start_date = models.DateField()

    class Meta:
        db_table = 'travel_project'
