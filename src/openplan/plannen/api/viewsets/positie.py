from django.db import transaction

import structlog
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from openplan.plannen.models.positie import Positie

from ..filtersets.positie import PositieFilter
from ..serializers.positie import PositieSerializer

logger = structlog.stdlib.get_logger(__name__)


@extend_schema(tags=["Positie"])
@extend_schema_view(
    list=extend_schema(
        summary="Alle posities opvragen.",
        description="Deze lijst kan gefilterd wordt met query-string parameters.",
    ),
    retrieve=extend_schema(
        summary="Een specifieke positie opvragen.",
        description="Een specifieke positie opvragen via UUID.",
    ),
    create=extend_schema(
        summary="Nieuwe positie aanmaken.",
        description="Voeg een nieuwe positie toe aan het systeem.",
    ),
    update=extend_schema(
        summary="Positie volledig bijwerken.",
        description="Werk alle gegevens van een positie bij.",
    ),
    partial_update=extend_schema(
        summary="Positie gedeeltelijk bijwerken.",
        description="Werk enkele gegevens van een positie bij.",
    ),
    destroy=extend_schema(
        summary="Positie verwijderen.",
        description="Verwijder een specifieke positie.",
    ),
)
class PositieViewSet(viewsets.ModelViewSet):
    queryset = Positie.objects.all()
    serializer_class = PositieSerializer
    filterset_class = PositieFilter
    lookup_field = "uuid"
    permission_classes = (IsAuthenticated,)

    @transaction.atomic
    def perform_create(self, serializer):
        super().perform_create(serializer)
        positie = serializer.instance
        logger.info(
            "positie_created",
            uuid=str(positie.uuid),
        )

    @transaction.atomic
    def perform_update(self, serializer):
        super().perform_update(serializer)
        positie = serializer.instance
        logger.info(
            "positie_updated",
            uuid=str(positie.uuid),
        )

    @transaction.atomic
    def perform_destroy(self, instance):
        super().perform_destroy(instance)
        logger.info(
            "positie_deleted",
            uuid=str(instance.uuid),
        )
