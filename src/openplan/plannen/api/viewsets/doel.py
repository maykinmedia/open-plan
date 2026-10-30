from django.db import transaction

import structlog
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from openplan.plannen.models.doel import Doel

from ...metrics import (
    doelen_create_counter,
    doelen_delete_counter,
    doelen_update_counter,
)
from ..filtersets.doel import DoelFilter
from ..serializers.doel import DoelSerializer

logger = structlog.stdlib.get_logger(__name__)


@extend_schema(tags=["Doel"])
@extend_schema_view(
    list=extend_schema(
        summary="Alle doelen opvragen.",
        description="Deze lijst kan gefilterd wordt met query-string parameters.",
    ),
    retrieve=extend_schema(
        summary="Een specifiek doel opvragen.",
        description="Een specifiek doel opvragen via UUID.",
    ),
    create=extend_schema(
        summary="Nieuw doel aanmaken.",
        description="Voeg een nieuw doel toe aan het systeem.",
    ),
    update=extend_schema(
        summary="Doel volledig bijwerken.",
        description="Werk alle gegevens van een doel bij.",
    ),
    partial_update=extend_schema(
        summary="Doel gedeeltelijk bijwerken.",
        description="Werk enkele gegevens van een doel bij.",
    ),
    destroy=extend_schema(
        summary="Doel verwijderen.",
        description="Verwijder een specifiek doel.",
    ),
)
class DoelViewSet(viewsets.ModelViewSet):
    queryset = Doel.objects.all()
    serializer_class = DoelSerializer
    filterset_class = DoelFilter
    lookup_field = "uuid"
    permission_classes = (IsAuthenticated,)

    @transaction.atomic
    def perform_create(self, serializer):
        super().perform_create(serializer)
        doel = serializer.instance
        logger.info(
            "doel_created",
            uuid=str(doel.uuid),
        )
        doelen_create_counter.add(1)

    @transaction.atomic
    def perform_update(self, serializer):
        super().perform_update(serializer)
        doel = serializer.instance
        logger.info(
            "doel_updated",
            uuid=str(doel.uuid),
        )
        doelen_update_counter.add(1)

    @transaction.atomic
    def perform_destroy(self, instance):
        super().perform_destroy(instance)
        logger.info(
            "doel_deleted",
            uuid=str(instance.uuid),
        )
        doelen_delete_counter.add(1)
