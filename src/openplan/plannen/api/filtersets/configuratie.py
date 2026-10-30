from vng_api_common.filtersets import FilterSet

from openplan.plannen.models.configuratie import Configuratie


class ConfiguratieFilter(FilterSet):
    class Meta:
        model = Configuratie
        fields = {
            "domein__uuid": ["exact"],
            "naam": ["exact", "icontains"],
            "omschrijving": ["icontains"],
            "status": ["exact"],
        }
