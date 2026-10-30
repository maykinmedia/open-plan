from vng_api_common.filtersets import FilterSet

from openplan.plannen.models.positietype import PositieType


class PositietypeFilter(FilterSet):
    class Meta:
        model = PositieType
        fields = {
            "naam": ["exact", "icontains"],
            "omschrijving": ["icontains"],
            "status": ["exact"],
        }
