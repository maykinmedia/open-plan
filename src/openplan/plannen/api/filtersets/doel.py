from vng_api_common.filtersets import FilterSet

from openplan.plannen.models.doel import Doel


class DoelFilter(FilterSet):
    class Meta:
        model = Doel
        fields = {
            "persoon__uuid": ["exact"],
            "status": ["exact", "in"],
            "titel": ["exact", "icontains"],
            "startdatum": ["exact", "gte", "lte"],
            "einddatum": ["exact", "gte", "lte"],
            "resultaat": ["exact"],
        }
