from django.db import transaction

import structlog
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from openplan.plannen.models.configuratie import Configuratie

from ..filtersets.configuratie import ConfiguratieFilter
from ..serializers.configuratie import ConfiguratieSerializer

logger = structlog.stdlib.get_logger(__name__)


@extend_schema(tags=["Configuratie"])
@extend_schema_view(
    list=extend_schema(
        summary="Alle configuraties opvragen.",
        description="Deze lijst kan gefilterd wordt met query-string parameters.",
    ),
    retrieve=extend_schema(
        summary="Een specifieke configuratie opvragen.",
        description="Een specifieke configuratie opvragen via UUID.",
    ),
    create=extend_schema(
        summary="Nieuwe configuratie aanmaken.",
        description="Voeg een nieuwe configuratie toe aan het systeem.",
    ),
    update=extend_schema(
        summary="Configuratie volledig bijwerken.",
        description="Werk alle gegevens van een configuratie bij.",
    ),
    partial_update=extend_schema(
        summary="Configuratie gedeeltelijk bijwerken.",
        description="Werk enkele gegevens van een configuratie bij.",
    ),
    destroy=extend_schema(
        summary="Configuratie verwijderen.",
        description="Verwijder een specifieke configuratie.",
    ),
)
class ConfiguratieViewSet(viewsets.ModelViewSet):
    queryset = Configuratie.objects.all()
    serializer_class = ConfiguratieSerializer
    filterset_class = ConfiguratieFilter
    lookup_field = "uuid"
    permission_classes = (IsAuthenticated,)

    @transaction.atomic
    def perform_create(self, serializer):
        super().perform_create(serializer)
        configuratie = serializer.instance
        logger.info(
            "configuratie_created",
            uuid=str(configuratie.uuid),
        )

    @transaction.atomic
    def perform_update(self, serializer):
        super().perform_update(serializer)
        configuratie = serializer.instance
        logger.info(
            "configuratie_updated",
            uuid=str(configuratie.uuid),
        )

    @transaction.atomic
    def perform_destroy(self, instance):
        super().perform_destroy(instance)
        logger.info(
            "configuratie_deleted",
            uuid=str(instance.uuid),
        )
