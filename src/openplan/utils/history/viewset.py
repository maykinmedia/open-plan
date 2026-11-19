from collections.abc import Callable
from typing import Any

from django.core.exceptions import ImproperlyConfigured, ValidationError
from django.http import Http404
from django.shortcuts import get_object_or_404

from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import serializers
from rest_framework.decorators import action
from rest_framework.response import Response
from vng_api_common.exceptions import Gone

from .serializers import HistorieLijstSerializer

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
                f"Alle versies van een {naam}, de nieuwste eerst, met per versie "
                "de reden van de wijziging. De gegevens van een versie staan in "
                "het detail-endpoint, via versieUuid."
            ),
            responses=HistorieLijstSerializer(many=True),
        ),
        "history_detail": extend_schema(
            operation_id=f"{model_naam}_history_retrieve",
            summary=f"Een specifieke versie van een {naam} opvragen.",
            description=(
                f"Eén versie uit de historie van een {naam}, via versieUuid. "
                f"Is het {naam} verwijderd, dan zijn de gegevens gemaskeerd."
            ),
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

    After the object is deleted:
      GET/PUT/PATCH/DELETE /{uuid}/       410 Gone (instead of 404)
      history endpoints                   still work; data masked, reasons visible

    Set on the viewset:
      history_serializer_class  e.g. DoelHistorieSerializer
      history_select_related    e.g. ("doeltype",), for nested fields

    The required reason on update is handled by WijzigingSerializerMixin.
    """

    history_serializer_class: type[serializers.ModelSerializer] | None = None
    history_select_related: tuple[str, ...] = ()

    def get_serializer_class(self):
        action = getattr(self, "action", None)
        if action == "history":
            return HistorieLijstSerializer
        if action == "history_detail":
            if self.history_serializer_class is None:
                raise ImproperlyConfigured(
                    f"{self.__class__.__name__} should set history_serializer_class."
                )
            return self.history_serializer_class
        return super().get_serializer_class()

    def get_object(self):
        """404 for unknown objects, 410 Gone for deleted ones."""
        try:
            return super().get_object()
        except Http404:
            if self._verwijderde_historie().exists():
                raise Gone()
            raise

    def _verwijderde_historie(self):
        """History rows of the object in the URL, if it has been deleted."""
        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field
        lookup = {self.lookup_field: self.kwargs[lookup_url_kwarg]}
        model = self.get_queryset().model

        try:
            records = model.history.filter(**lookup)
            # Only counts as deleted if there is a "-" (deleted) version.
            if not records.filter(history_type="-").exists():
                return model.history.none()
        except (ValueError, ValidationError):
            return model.history.none()
        return records

    def _historie(self):
        """
        The history of the object in the URL, and whether to mask it.

        - Existing object: not masked.
        - Deleted object: masked. Looked up directly in the history table.
        - Unknown object: 404 (from get_object()).

        Returns a tuple (records, gemaskeerd).
        """
        try:
            obj = self.get_object()
        except Gone:
            records, gemaskeerd = self._verwijderde_historie(), True
        else:
            records, gemaskeerd = obj.history.all(), False

        return records.select_related(*self.history_select_related), gemaskeerd

    def _historie_serializer(self, *args, gemaskeerd: bool, **kwargs):
        """get_serializer() with "gemaskeerd" in the context, for HistorieSerializer."""
        context = {**self.get_serializer_context(), "gemaskeerd": gemaskeerd}
        return self.get_serializer(*args, context=context, **kwargs)

    @action(detail=True, methods=["get"])
    def history(self, request, *args, **kwargs):
        records, _gemaskeerd = self._historie()
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
        records, gemaskeerd = self._historie()
        # versie_uuid in the API is the history_id column in the database.
        record = get_object_or_404(records, history_id=versie_uuid)
        return Response(self._historie_serializer(record, gemaskeerd=gemaskeerd).data)
