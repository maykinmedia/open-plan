from django.db import transaction

import structlog
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from openplan.plannen.models.doeltype import DoelType

from ...metrics import (
    doeltypen_create_counter,
    doeltypen_delete_counter,
    doeltypen_update_counter,
)
from ..serializers.doeltype import DoelTypeSerializer

logger = structlog.stdlib.get_logger(__name__)


@extend_schema(tags=["Doeltype"])
@extend_schema_view(
    list=extend_schema(
        summary="Alle doeltypen opvragen.",
        description="Deze lijst kan gefilterd wordt met query-string parameters.",
    ),
    retrieve=extend_schema(
        summary="Een specifiek doeltype opvragen.",
        description="Een specifiek doeltype opvragen via UUID.",
    ),
    create=extend_schema(
        summary="Nieuw doeltype aanmaken.",
        description="Voeg een nieuw doeltype toe aan het systeem.",
    ),
    update=extend_schema(
        summary="Doeltype volledig bijwerken.",
        description="Werk alle gegevens van een doeltype bij.",
    ),
    partial_update=extend_schema(
        summary="Doeltype gedeeltelijk bijwerken.",
        description="Werk enkele gegevens van een doeltype bij.",
    ),
    destroy=extend_schema(
        summary="Doeltype verwijderen.",
        description="Verwijder een specifiek doeltype.",
    ),
)
class DoelTypeViewSet(viewsets.ModelViewSet):
    queryset = DoelType.objects.all()
    serializer_class = DoelTypeSerializer
    filterset_fields = {
        "doel_type",
    }
    lookup_field = "uuid"
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    @transaction.atomic
    def perform_create(self, serializer):
        super().perform_create(serializer)
        doeltype = serializer.instance
        logger.info(
            "doeltype_created",
            uuid=str(doeltype.uuid),
        )
        doeltypen_create_counter.add(1)

    @transaction.atomic
    def perform_update(self, serializer):
        super().perform_update(serializer)
        doeltype = serializer.instance
        logger.info(
            "doeltype_updated",
            uuid=str(doeltype.uuid),
        )
        doeltypen_update_counter.add(1)

    @transaction.atomic
    def perform_destroy(self, instance):
        super().perform_destroy(instance)
        logger.info(
            "doeltype_deleted",
            uuid=str(instance.uuid),
        )
        doeltypen_delete_counter.add(1)
