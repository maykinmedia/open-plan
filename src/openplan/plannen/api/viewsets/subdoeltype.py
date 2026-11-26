from django.db import transaction

import structlog
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from openplan.plannen.models.subdoeltype import SubdoelType
from openplan.utils.mixins import ProtectedDestroyMixin

from ..filtersets.subdoeltype import SubdoeltypeFilter
from ..serializers.subdoeltype import SubdoeltypeSerializer

logger = structlog.stdlib.get_logger(__name__)


@extend_schema(tags=["Subdoeltype"])
@extend_schema_view(
    list=extend_schema(
        summary="Alle subdoeltypen opvragen.",
        description="Deze lijst kan gefilterd wordt met query-string parameters.",
    ),
    retrieve=extend_schema(
        summary="Een specifiek subdoeltype opvragen.",
        description="Een specifiek subdoeltype opvragen via UUID.",
    ),
    create=extend_schema(
        summary="Nieuw subdoeltype aanmaken.",
        description="Voeg een nieuw subdoeltype toe aan het systeem.",
    ),
    update=extend_schema(
        summary="Subdoeltype volledig bijwerken.",
        description="Werk alle gegevens van een subdoeltype bij.",
    ),
    partial_update=extend_schema(
        summary="Subdoeltype gedeeltelijk bijwerken.",
        description="Werk enkele gegevens van een subdoeltype bij.",
    ),
    destroy=extend_schema(
        summary="Subdoeltype verwijderen.",
        description="Verwijder een specifiek subdoeltype.",
    ),
)
class SubdoelTypeViewSet(ProtectedDestroyMixin, viewsets.ModelViewSet):
    queryset = SubdoelType.objects.prefetch_related("configuraties").order_by("naam")
    serializer_class = SubdoeltypeSerializer
    filterset_class = SubdoeltypeFilter
    lookup_field = "uuid"
    permission_classes = (IsAuthenticated,)

    @transaction.atomic
    def perform_create(self, serializer):
        super().perform_create(serializer)
        subdoeltype = serializer.instance
        logger.info(
            "subdoeltype_created",
            uuid=str(subdoeltype.uuid),
        )

    @transaction.atomic
    def perform_update(self, serializer):
        super().perform_update(serializer)
        subdoeltype = serializer.instance
        logger.info(
            "subdoeltype_updated",
            uuid=str(subdoeltype.uuid),
        )

    @transaction.atomic
    def perform_destroy(self, instance):
        super().perform_destroy(instance)
        logger.info(
            "subdoeltype_deleted",
            uuid=str(instance.uuid),
        )
