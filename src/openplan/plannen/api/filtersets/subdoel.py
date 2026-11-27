from vng_api_common.filtersets import FilterSet

from openplan.plannen.models.subdoel import Subdoel


class SubdoelFilter(FilterSet):
    class Meta:
        model = Subdoel
        fields = {
            "doel__uuid": ["exact"],
            "status": ["exact"],
            "voortgang": ["exact"],
            "naam": ["exact", "icontains"],
            "omschrijving": ["icontains"],
            "startdatum": ["exact", "gte", "lte"],
            "einddatum": ["exact", "gte", "lte"],
            "beoogde_startdatum": ["exact", "gte", "lte"],
            "beoogde_einddatum": ["exact", "gte", "lte"],
        }
