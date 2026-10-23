from vng_api_common.filtersets import FilterSet

from openplan.plannen.models.plan import Plan


class PlanFilter(FilterSet):
    class Meta:
        model = Plan
        fields = {
            "status": ["exact"],
            "naam": ["exact", "icontains"],
            "eigenaar": ["exact"],
            "zaak": ["exact"],
            "contactmoment": ["exact"],
            "startdatum": ["exact", "gte", "lte"],
            "einddatum": ["exact", "gte", "lte"],
        }
