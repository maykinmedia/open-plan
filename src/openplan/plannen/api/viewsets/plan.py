from django.db import transaction

import structlog
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from openplan.plannen.models.plan import Plan

from ...metrics import (
    plannen_create_counter,
    plannen_delete_counter,
    plannen_update_counter,
)
from ..filtersets.plan import PlanFilter
from ..serializers.plan import PlanSerializer

logger = structlog.stdlib.get_logger(__name__)


@extend_schema(tags=["Plan"])
@extend_schema_view(
    list=extend_schema(
        summary="Alle plannen opvragen.",
        description="Deze lijst kan gefilterd wordt met query-string parameters.",
    ),
    retrieve=extend_schema(
        summary="Een specifiek plan opvragen.",
        description="Een specifiek plan opvragen via UUID.",
    ),
    create=extend_schema(
        summary="Nieuw plan aanmaken.",
        description="Voeg een nieuw plan toe aan het systeem.",
    ),
    update=extend_schema(
        summary="Plan volledig bijwerken.",
        description="Werk alle gegevens van een plan bij.",
    ),
    partial_update=extend_schema(
        summary="Plan gedeeltelijk bijwerken.",
        description="Werk enkele gegevens van een plan bij.",
    ),
    destroy=extend_schema(
        summary="Plan verwijderen.",
        description="Verwijder een specifiek plan.",
    ),
)
class PlanViewSet(viewsets.ModelViewSet):
    queryset = Plan.objects.all()
    serializer_class = PlanSerializer
    filterset_class = PlanFilter
    lookup_field = "uuid"
    permission_classes = (IsAuthenticated,)

    @transaction.atomic
    def perform_create(self, serializer):
        super().perform_create(serializer)
        plan = serializer.instance
        logger.info(
            "plan_created",
            uuid=str(plan.uuid),
        )
        plannen_create_counter.add(1)

    @transaction.atomic
    def perform_update(self, serializer):
        super().perform_update(serializer)
        plan = serializer.instance
        logger.info(
            "plan_updated",
            uuid=str(plan.uuid),
        )
        plannen_update_counter.add(1)

    @transaction.atomic
    def perform_destroy(self, instance):
        super().perform_destroy(instance)
        logger.info(
            "plan_deleted",
            uuid=str(instance.uuid),
        )
        plannen_delete_counter.add(1)
