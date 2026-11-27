from vng_api_common.filtersets import FilterSet

from openplan.plannen.models.evaluatie import Evaluatie


class EvaluatieFilter(FilterSet):
    class Meta:
        model = Evaluatie
        fields = {
            "plan__uuid": ["exact"],
            "naam": ["exact", "icontains"],
            "omschrijving": ["icontains"],
            "status": ["exact"],
            "datum": ["exact", "gte", "lte"],
            "eigenaar": ["exact"],
            "zaak": ["exact"],
            "verslag": ["exact"],
            "contactmoment": ["exact"],
        }
