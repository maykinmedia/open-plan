from django.db import transaction

import structlog
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from openplan.plannen.models.positietype import PositieType

from ..filtersets.positietype import PositietypeFilter
from ..serializers.positietype import PositietypeSerializer

logger = structlog.stdlib.get_logger(__name__)


@extend_schema(tags=["Positietype"])
@extend_schema_view(
    list=extend_schema(
        summary="Alle positietypes opvragen.",
        description="Deze lijst kan gefilterd wordt met query-string parameters.",
    ),
    retrieve=extend_schema(
        summary="Een specifieke positietype opvragen.",
        description="Een specifieke positie opvragen via UUID.",
    ),
    create=extend_schema(
        summary="Nieuwe positietype aanmaken.",
        description="Voeg een nieuwe positietype toe aan het systeem.",
    ),
    update=extend_schema(
        summary="Positietype volledig bijwerken.",
        description="Werk alle gegevens van een positietype bij.",
    ),
    partial_update=extend_schema(
        summary="Positietype gedeeltelijk bijwerken.",
        description="Werk enkele gegevens van een positietype bij.",
    ),
    destroy=extend_schema(
        summary="Positietype verwijderen.",
        description="Verwijder een specifieke positietype.",
    ),
)
class PositietypeViewSet(viewsets.ModelViewSet):
    queryset = PositieType.objects.all()
    serializer_class = PositietypeSerializer
    filterset_class = PositietypeFilter
    lookup_field = "uuid"
    permission_classes = (IsAuthenticated,)

    @transaction.atomic
    def perform_create(self, serializer):
        super().perform_create(serializer)
        positietype = serializer.instance
        logger.info(
            "positietype_created",
            uuid=str(positietype.uuid),
        )

    @transaction.atomic
    def perform_update(self, serializer):
        super().perform_update(serializer)
        positietype = serializer.instance
        logger.info(
            "positietype_updated",
            uuid=str(positietype.uuid),
        )

    @transaction.atomic
    def perform_destroy(self, instance):
        super().perform_destroy(instance)
        logger.info(
            "positietype_deleted",
            uuid=str(instance.uuid),
        )
