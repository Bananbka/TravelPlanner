from django.core.exceptions import ValidationError
from django.db import models

from apps.core.models import TimeStampedModel


class TravelProject(TimeStampedModel):
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='projects')
    name = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)
    start_date = models.DateField(blank=True, null=True)

    class Meta:
        db_table = 'travel_project'

    @property
    def is_completed(self) -> bool:
        places = self.places.all()
        if not places.exists():
            return False
        return all(place.is_visited for place in places)

    def delete(self, *args, **kwargs):
        if self.places.filter(is_visited=True).exists():
            raise ValidationError("Cannot delete a project that has visited places.")
        return super().delete(*args, **kwargs)
