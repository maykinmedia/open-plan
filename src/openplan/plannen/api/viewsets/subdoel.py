from django.db import transaction

import structlog
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from openplan.plannen.models.subdoel import Subdoel

# from ...metrics import (
#     doelen_create_counter,
#     doelen_delete_counter,
#     doelen_update_counter,
# )
from ..filtersets.subdoel import SubdoelFilter
from ..serializers.subdoel import SubdoelSerializer

logger = structlog.stdlib.get_logger(__name__)


@extend_schema(tags=["Subdoel"])
@extend_schema_view(
    list=extend_schema(
        summary="Alle subdoelen opvragen.",
        description="Deze lijst kan gefilterd wordt met query-string parameters.",
    ),
    retrieve=extend_schema(
        summary="Een specifiek subdoel opvragen.",
        description="Een specifiek subdoel opvragen via UUID.",
    ),
    create=extend_schema(
        summary="Nieuw subdoel aanmaken.",
        description="Voeg een nieuw subdoel toe aan het systeem.",
    ),
    update=extend_schema(
        summary="Subdoel volledig bijwerken.",
        description="Werk alle gegevens van een subdoel bij.",
    ),
    partial_update=extend_schema(
        summary="Subdoel gedeeltelijk bijwerken.",
        description="Werk enkele gegevens van een subdoel bij.",
    ),
    destroy=extend_schema(
        summary="Subdoel verwijderen.",
        description="Verwijder een specifiek subdoel.",
    ),
)
class SubdoelViewSet(viewsets.ModelViewSet):
    queryset = Subdoel.objects.select_related("doel", "subdoeltype").order_by(
        "naam", "uuid"
    )
    serializer_class = SubdoelSerializer
    filterset_class = SubdoelFilter
    lookup_field = "uuid"
    permission_classes = (IsAuthenticated,)

    @transaction.atomic
    def perform_create(self, serializer):
        super().perform_create(serializer)
        subdoel = serializer.instance
        logger.info(
            "subdoel_created",
            uuid=str(subdoel.uuid),
        )
        # doelen_create_counter.add(1)

    @transaction.atomic
    def perform_update(self, serializer):
        super().perform_update(serializer)
        subdoel = serializer.instance
        logger.info(
            "subdoel_updated",
            uuid=str(subdoel.uuid),
        )
        # doelen_update_counter.add(1)

    @transaction.atomic
    def perform_destroy(self, instance):
        super().perform_destroy(instance)
        logger.info(
            "subdoel_deleted",
            uuid=str(instance.uuid),
        )
        # doelen_delete_counter.add(1)
