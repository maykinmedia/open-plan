from vng_api_common.filtersets import FilterSet

from openplan.plannen.models.evaluatie import Evaluatie


class EvaluatieFilter(FilterSet):
    class Meta:
        model = Evaluatie
        fields = {
            "plan__uuid": ["exact"],
            "status": ["exact"],
            "datum": ["exact", "gte", "lte"],
            "eigenaar": ["exact"],
            "zaak": ["exact"],
            "document": ["exact"],
            "contactmoment": ["exact"],
        }
