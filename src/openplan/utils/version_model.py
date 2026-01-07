from django.db import models

from pghistory import ContextJSONField


class VersionedModel(models.Model):
    version_context = ContextJSONField(null=True, blank=True)

    class Meta:
        abstract = True
