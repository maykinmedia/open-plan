from django.db import transaction

import structlog
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from openplan.plannen.models.subject import Subject

from ...metrics import (
    subjecten_create_counter,
    subjecten_delete_counter,
    subjecten_update_counter,
)
from ..serializers.subject import SubjectSerializer

logger = structlog.stdlib.get_logger(__name__)


@extend_schema(tags=["Subject"])
@extend_schema_view(
    list=extend_schema(
        summary="Alle subjecten opvragen.",
        description="Deze lijst kan gefilterd wordt met query-string parameters.",
    ),
    retrieve=extend_schema(
        summary="Een specifiek subject opvragen.",
        description="Een specifiek subject opvragen via UUID.",
    ),
    create=extend_schema(
        summary="Nieuw subject aanmaken.",
        description="Voeg een nieuw subject toe aan het systeem.",
    ),
    update=extend_schema(
        summary="Subject volledig bijwerken.",
        description="Werk alle gegevens van een subject bij.",
    ),
    partial_update=extend_schema(
        summary="Subject gedeeltelijk bijwerken.",
        description="Werk enkele gegevens van een subject bij.",
    ),
    destroy=extend_schema(
        summary="Subject verwijderen.",
        description="Verwijder een specifiek subject.",
    ),
)
class SubjectViewSet(viewsets.ModelViewSet):
    queryset = Subject.objects.all()
    serializer_class = SubjectSerializer
    lookup_field = "uuid"
    permission_classes = (IsAuthenticated,)

    @transaction.atomic
    def perform_create(self, serializer):
        super().perform_create(serializer)
        subject = serializer.instance
        logger.info(
            "subject_created",
            uuid=str(subject.uuid),
        )
        subjecten_create_counter.add(1)

    @transaction.atomic
    def perform_update(self, serializer):
        super().perform_update(serializer)
        subject = serializer.instance
        logger.info(
            "subject_updated",
            uuid=str(subject.uuid),
        )
        subjecten_update_counter.add(1)

    @transaction.atomic
    def perform_destroy(self, instance):
        super().perform_destroy(instance)
        logger.info(
            "subject_deleted",
            uuid=str(instance.uuid),
        )
        subjecten_delete_counter.add(1)
