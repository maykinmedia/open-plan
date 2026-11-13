from django.shortcuts import get_object_or_404

from rest_framework.decorators import action
from rest_framework.response import Response

from .serializers import history_serializer_voor


class HistorieViewSetMixin:
    """
    Use as: class DoelViewSet(HistorieViewSetMixin, viewsets.ModelViewSet)

      PUT/PATCH /{id}/                       reden_wijziging required
      GET       /{id}/history/               all states, newest first
      GET       /{id}/history/{history_id}/  one state
    """

    def perform_create(self, serializer):
        # No reason on create; the history row gets REGISTREREN.
        serializer.validated_data.pop("reden_wijziging", None)
        serializer.validated_data.pop("toelichting_reden", None)
        serializer.save()

    def perform_update(self, serializer):
        # Pop so they aren't set as model fields; the signal reads them
        # from the instance when the history row is created.
        instance = serializer.instance
        instance._reden_wijziging = serializer.validated_data.pop("reden_wijziging")
        instance._toelichting_reden = serializer.validated_data.pop(
            "toelichting_reden", ""
        )
        serializer.save()

    def _historie_serializer(self):
        return history_serializer_voor(self.get_queryset().model)

    @action(detail=True, methods=["get"])
    def history(self, request, *args, **kwargs):
        records = self.get_object().history.select_related("history_user")
        serializer_class = self._historie_serializer()
        page = self.paginate_queryset(records)
        if page is not None:
            return self.get_paginated_response(serializer_class(page, many=True).data)
        return Response(serializer_class(records, many=True).data)

    @action(detail=True, methods=["get"], url_path=r"history/(?P<history_id>[^/.]+)")
    def history_detail(self, request, history_id=None, *args, **kwargs):
        record = get_object_or_404(
            self.get_object().history.all(), history_id=history_id
        )
        return Response(self._historie_serializer()(record).data)
