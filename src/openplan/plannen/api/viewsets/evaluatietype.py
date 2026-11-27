from django.db import transaction

import structlog
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from openplan.plannen.api.filtersets.evaluatietype import EvaluatietypeFilter
from openplan.plannen.models.evaluatietype import Evaluatietype
from openplan.utils.mixins import ProtectedDestroyMixin

from ..serializers.evaluatietype import EvaluatietypeSerializer

logger = structlog.stdlib.get_logger(__name__)


@extend_schema(tags=["Evaluatietype"])
@extend_schema_view(
    list=extend_schema(
        summary="Alle evaluatietypes opvragen.",
        description="Deze lijst kan gefilterd wordt met query-string parameters.",
    ),
    retrieve=extend_schema(
        summary="Een specifiek evaluatietype opvragen.",
        description="Een specifiek evaluatietype opvragen via UUID.",
    ),
    create=extend_schema(
        summary="Nieuw evaluatietype aanmaken.",
        description="Voeg een nieuw evaluatietype toe aan het systeem.",
    ),
    update=extend_schema(
        summary="Evaluatietype volledig bijwerken.",
        description="Werk alle gegevens van een evaluatietype bij.",
    ),
    partial_update=extend_schema(
        summary="Evaluatietype gedeeltelijk bijwerken.",
        description="Werk enkele gegevens van een evaluatietype bij.",
    ),
    destroy=extend_schema(
        summary="Evaluatietype verwijderen.",
        description="Verwijder een specifiek evaluatietype.",
    ),
)
class EvaluatietypeViewSet(ProtectedDestroyMixin, viewsets.ModelViewSet):
    queryset = Evaluatietype.objects.prefetch_related("configuraties").order_by("naam")
    serializer_class = EvaluatietypeSerializer
    filterset_class = EvaluatietypeFilter
    lookup_field = "uuid"
    permission_classes = (IsAuthenticated,)

    @transaction.atomic
    def perform_create(self, serializer):
        super().perform_create(serializer)
        evaluatietype = serializer.instance
        logger.info(
            "evaluatietype_created",
            uuid=str(evaluatietype.uuid),
        )

    @transaction.atomic
    def perform_update(self, serializer):
        super().perform_update(serializer)
        evaluatietype = serializer.instance
        logger.info(
            "evaluatietype_updated",
            uuid=str(evaluatietype.uuid),
        )

    @transaction.atomic
    def perform_destroy(self, instance):
        super().perform_destroy(instance)
        logger.info(
            "evaluatietype_deleted",
            uuid=str(instance.uuid),
        )
