from vng_api_common.filtersets import FilterSet

from openplan.plannen.models.domein import Domein


class DomeinFilter(FilterSet):
    class Meta:
        model = Domein
        fields = {
            "naam": ["exact", "icontains"],
            "omschrijving": ["icontains"],
            "status": ["exact"],
        }
