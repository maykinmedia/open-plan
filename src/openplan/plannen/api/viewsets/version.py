from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from openplan.plannen.api.serializers.version import VersionSerializer
from openplan.plannen.models.version import Version


@extend_schema(tags=["Planversies"])
@extend_schema_view(
    list=extend_schema(
        summary="Alle versies van een plan opvragen.",
        description="Geeft een overzicht van alle opgeslagen versies voor een specifiek plan.",
    ),
    retrieve=extend_schema(
        summary="Een specifieke planversie opvragen.",
        description="Haal één specifieke versie van een plan op inclusief snapshot.",
    ),
)
class PlanVersionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Version.objects.all()
    serializer_class = VersionSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    lookup_field = "id"

    def get_queryset(self):
        plan_id = self.kwargs.get("plan_id")

        return (
            Version.objects.filter(plan_id=plan_id)
            .select_related("actor", "plan")
            .order_by("-created_at")
        )
