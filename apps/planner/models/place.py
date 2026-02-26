from django.db import models

from apps.core.models import TimeStampedModel


class Place(TimeStampedModel):
    project = models.ForeignKey('planner.TravelProject', on_delete=models.CASCADE, related_name='places')
    external_id = models.CharField()

    notes = models.TextField(blank=True, null=True)
    is_visited = models.BooleanField(default=False)

    class Meta:
        db_table = 'place'
        unique_together = (('project', 'external_id'),)
