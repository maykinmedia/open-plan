from django.db import transaction

from pghistory import context

from openplan.plannen.models.version import Version

from .version_snapshot import build_snapshot


def with_plan_version(*, plan, user, comment, fn):
    with transaction.atomic():
        version = Version.objects.create(
            plan=plan,
            actor=user,
            comment=comment,
        )

        with context(version_context={"version_id": version.id}):
            result = fn()

        version.snapshot = build_snapshot(plan)
        version.save()

        return result
