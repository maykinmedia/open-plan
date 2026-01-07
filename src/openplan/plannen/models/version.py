from django.db import models
from django.utils.translation import gettext_lazy as _

from pghistory import ContextJSONField

from openplan.plannen.models.plan import Plan


class Version(models.Model):
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE, related_name="versies")
    actor = models.ForeignKey("accounts.User", null=True, on_delete=models.SET_NULL)
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    snapshot = models.JSONField(null=True, blank=True)

    class Meta:
        verbose_name = _("Version")
        verbose_name_plural = _("Versions")

    def __str__(self):
        return f"{self.plan} - {self.actor} - {self.created_at}"


class VersionedModel(models.Model):
    version_context = ContextJSONField(null=True, blank=True)

    class Meta:
        abstract = True
