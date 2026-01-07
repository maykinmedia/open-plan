from django.db import transaction

from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from openplan.plannen.models.plan import Plan
from openplan.utils.version_mixin import with_plan_version

from ..filtersets.plan import PlanFilter
from ..serializers.plan import PlanSerializer


@extend_schema(tags=["Plan"])
@extend_schema_view(
    list=extend_schema(
        summary="Alle plannen opvragen.",
        description="Deze lijst kan gefilterd wordt met query-string parameters.",
    ),
    retrieve=extend_schema(
        summary="Een specifiek plan opvragen.",
        description="Een specifiek plan opvragen via UUID.",
    ),
    create=extend_schema(
        summary="Nieuw plan aanmaken.",
        description="Voeg een nieuw plan toe aan het systeem.",
    ),
    update=extend_schema(
        summary="Plan volledig bijwerken.",
        description="Werk alle gegevens van een plan bij.",
    ),
    partial_update=extend_schema(
        summary="Plan gedeeltelijk bijwerken.",
        description="Werk enkele gegevens van een plan bij.",
    ),
    destroy=extend_schema(
        summary="Plan verwijderen.",
        description="Verwijder een specifiek plan.",
    ),
)
class PlanViewSet(viewsets.ModelViewSet):
    queryset = Plan.objects.all()
    serializer_class = PlanSerializer
    filterset_class = PlanFilter
    lookup_field = "uuid"
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    @transaction.atomic
    def perform_create(self, serializer):
        super().perform_create(serializer)

        plan = serializer.instance

        with_plan_version(
            plan=plan,
            user=self.request.user,
            comment="Plan created via API",
            fn=lambda: None,
        )

    @transaction.atomic
    def perform_update(self, serializer):
        super().perform_update(serializer)

        plan = serializer.save()
        with_plan_version(
            plan=plan,
            user=self.request.user,
            comment="Plan updated via API",
            fn=lambda: None,
        )
