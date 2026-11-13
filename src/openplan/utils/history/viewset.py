from collections.abc import Callable
from typing import Any

from django.core.exceptions import ImproperlyConfigured
from django.shortcuts import get_object_or_404

from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import serializers
from rest_framework.decorators import action
from rest_framework.response import Response

HISTORIE_ACTIES = ("history", "history_detail")


def historie_schema(
    serializer_class: type[serializers.ModelSerializer], naam: str
) -> dict[str, Callable[..., Any]]:
    """
    Schema for the history endpoints of one viewset. Use in extend_schema_view:

        @extend_schema_view(
            list=extend_schema(...),
            **historie_schema(DoelHistorieSerializer, "doel"),
        )
    """
    model_naam = serializer_class.Meta.model.instance_type._meta.model_name

    return {
        "history": extend_schema(
            operation_id=f"{model_naam}_history_list",
            summary=f"Historie van een {naam} opvragen.",
            description=(
                f"Alle versies van een {naam}, de nieuwste eerst. Elke versie bevat "
                "de gegevens zoals ze na die wijziging waren en de reden van de wijziging."
            ),
            responses=serializer_class(many=True),
        ),
        "history_detail": extend_schema(
            operation_id=f"{model_naam}_history_retrieve",
            summary=f"Een specifieke versie van een {naam} opvragen.",
            description=f"Eén versie uit de historie van een {naam}, via historyId.",
            parameters=[
                OpenApiParameter(
                    name="versie_uuid",
                    type=OpenApiTypes.UUID,
                    location=OpenApiParameter.PATH,
                    description="UUID van de versie (versieUuid uit de historie-lijst).",
                )
            ],
            responses=serializer_class,
        ),
    }


class HistorieViewSetMixin:
    """
    Use as: class DoelViewSet(HistorieViewSetMixin, viewsets.ModelViewSet)

      GET /{uuid}/history/                all versions, newest first
      GET /{uuid}/history/{versie_uuid}/  one version

    Set on the viewset:
      history_serializer_class  e.g. DoelHistorieSerializer
      history_select_related    e.g. ("doeltype",), for nested fields

    The required reason on update is handled by WijzigingSerializerMixin.
    """

    history_serializer_class: type[serializers.ModelSerializer] | None = None
    history_select_related: tuple[str, ...] = ()

    def get_serializer_class(self):
        if getattr(self, "action", None) in HISTORIE_ACTIES:
            if self.history_serializer_class is None:
                raise ImproperlyConfigured(
                    f"{self.__class__.__name__} should set history_serializer_class."
                )
            return self.history_serializer_class
        return super().get_serializer_class()

    def _historie(self):
        return self.get_object().history.select_related(*self.history_select_related)

    @action(detail=True, methods=["get"])
    def history(self, request, *args, **kwargs):
        records = self._historie()
        page = self.paginate_queryset(records)
        if page is not None:
            return self.get_paginated_response(
                self.get_serializer(page, many=True).data
            )
        return Response(self.get_serializer(records, many=True).data)

    @action(
        detail=True,
        methods=["get"],
        url_path=r"history/(?P<versie_uuid>[0-9a-f-]{36})",
    )
    def history_detail(self, request, versie_uuid=None, *args, **kwargs):
        # versie_uuid in the API is the history_id column in the database.
        record = get_object_or_404(self._historie(), history_id=versie_uuid)
        return Response(self.get_serializer(record).data)
