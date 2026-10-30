from vng_api_common.filtersets import FilterSet

from openplan.plannen.models.positie import Positie


class PositieFilter(FilterSet):
    class Meta:
        model = Positie
        fields = {
            "subject__uuid": ["exact"],
            "positietype__uuid": ["exact"],
            "status": ["exact"],
            "naam": ["exact", "icontains"],
            "omschrijving": ["icontains"],
        }
