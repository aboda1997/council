from django.db import models
from django.utils import timezone


class BaseDbModel(models.Model):
    """
    An abstract base class that adds few standard fields used in most db tables.
    """

    createdAt = models.DateTimeField(default=timezone.now, blank=True)
    createdBy = models.IntegerField(default=0, blank=True)
    updatedAt = models.DateTimeField(null=True)
    updatedBy = models.IntegerField(null=True)

    class Meta:
        abstract = True
