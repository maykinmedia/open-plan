from django.db import transaction

import structlog
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from openplan.plannen.models.domein import Domein

from ..filtersets.domein import DomeinFilter
from ..serializers.domein import DomeinSerializer

logger = structlog.stdlib.get_logger(__name__)


@extend_schema(tags=["Domein"])
@extend_schema_view(
    list=extend_schema(
        summary="Alle domeinen opvragen.",
        description="Deze lijst kan gefilterd wordt met query-string parameters.",
    ),
    retrieve=extend_schema(
        summary="Een specifiek domein opvragen.",
        description="Een specifiek domein opvragen via UUID.",
    ),
    create=extend_schema(
        summary="Nieuw domein aanmaken.",
        description="Voeg een nieuw domein toe aan het systeem.",
    ),
    update=extend_schema(
        summary="Domein volledig bijwerken.",
        description="Werk alle gegevens van een domein bij.",
    ),
    partial_update=extend_schema(
        summary="Domein gedeeltelijk bijwerken.",
        description="Werk enkele gegevens van een domein bij.",
    ),
    destroy=extend_schema(
        summary="Domein verwijderen.",
        description="Verwijder een specifiek domein.",
    ),
)
class DomeinViewSet(viewsets.ModelViewSet):
    queryset = Domein.objects.all()
    serializer_class = DomeinSerializer
    filterset_class = DomeinFilter
    lookup_field = "uuid"
    permission_classes = (IsAuthenticated,)

    @transaction.atomic
    def perform_create(self, serializer):
        super().perform_create(serializer)
        domein = serializer.instance
        logger.info(
            "domein_created",
            uuid=str(domein.uuid),
        )

    @transaction.atomic
    def perform_update(self, serializer):
        super().perform_update(serializer)
        domein = serializer.instance
        logger.info(
            "domein_updated",
            uuid=str(domein.uuid),
        )

    @transaction.atomic
    def perform_destroy(self, instance):
        super().perform_destroy(instance)
        logger.info(
            "domein_deleted",
            uuid=str(instance.uuid),
        )
