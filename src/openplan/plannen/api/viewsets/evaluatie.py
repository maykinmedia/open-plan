from django.db import transaction

import structlog
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from openplan.plannen.api.filtersets.evaluatie import EvaluatieFilter
from openplan.plannen.models.evaluatie import Evaluatie

from ...metrics import (
    contactmomenten_create_counter,
    contactmomenten_delete_counter,
    contactmomenten_update_counter,
)
from ..serializers.evaluatie import EvaluatieSerializer

logger = structlog.stdlib.get_logger(__name__)


@extend_schema(tags=["Evaluatie"])
@extend_schema_view(
    list=extend_schema(
        summary="Alle evaluaties opvragen.",
        description="Deze lijst kan gefilterd wordt met query-string parameters.",
    ),
    retrieve=extend_schema(
        summary="Een specifiek evaluatie opvragen.",
        description="Een specifiek evaluatie opvragen via UUID.",
    ),
    create=extend_schema(
        summary="Nieuw evaluatie aanmaken.",
        description="Voeg een nieuw evaluatie toe aan het systeem.",
    ),
    update=extend_schema(
        summary="Evaluatie volledig bijwerken.",
        description="Werk alle gegevens van een evaluatie bij.",
    ),
    partial_update=extend_schema(
        summary="Evaluatie gedeeltelijk bijwerken.",
        description="Werk enkele gegevens van een evaluatie bij.",
    ),
    destroy=extend_schema(
        summary="Evaluatie verwijderen.",
        description="Verwijder een specifiek evaluatie.",
    ),
)
class EvaluatieViewSet(viewsets.ModelViewSet):
    queryset = Evaluatie.objects.all()
    serializer_class = EvaluatieSerializer
    filterset_class = EvaluatieFilter
    lookup_field = "uuid"
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    @transaction.atomic
    def perform_create(self, serializer):
        super().perform_create(serializer)
        evaluatie = serializer.instance
        logger.info(
            "evaluatie_created",
            uuid=str(evaluatie.uuid),
        )
        contactmomenten_create_counter.add(1)

    @transaction.atomic
    def perform_update(self, serializer):
        super().perform_update(serializer)
        evaluatie = serializer.instance
        logger.info(
            "evaluatie_updated",
            uuid=str(evaluatie.uuid),
        )
        contactmomenten_update_counter.add(1)

    @transaction.atomic
    def perform_destroy(self, instance):
        super().perform_destroy(instance)
        logger.info(
            "evaluatie_deleted",
            uuid=str(instance.uuid),
        )
        contactmomenten_delete_counter.add(1)
